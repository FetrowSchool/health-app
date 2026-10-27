from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sqlite3
import tempfile
import unittest
from uuid import uuid4

from fastapi.testclient import TestClient
from backend.app.config import Settings
from backend.app.main import create_app
from backend.app.database import initialize_database


class ActivityTests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.path = Path(folder.name) / 'test.sqlite3'
        self.settings = Settings(database_path=self.path)
        self.client = self.enterContext(TestClient(create_app(self.settings)))
        self.app_id = str(uuid4())
        self.headers = {'X-App-ID': self.app_id}
        self.started = datetime(2026, 10, 19, 12, tzinfo=timezone.utc)

    def start(self, exercise='paced_breathing', session_id=None):
        payload = dict(id=session_id or str(uuid4()), exercise_type=exercise,
                       started_at=self.started.isoformat(), entry_duration_seconds=0.024)
        response = self.client.post('/api/sessions', headers=self.headers, json=payload)
        self.assertEqual(response.status_code, 200, response.text)
        return payload, response.json()

    def end_body(self, status='completed', duration=60.012):
        return dict(status=status, ended_at=(self.started + timedelta(seconds=duration)).isoformat(), duration_seconds=duration)

    def end(self, session_id, body=None):
        return self.client.patch('/api/sessions/' + session_id, headers=self.headers, json=body or self.end_body())

    def test_start_complete_feedback_are_one_record_and_idempotent(self):
        payload, session = self.start()
        self.assertEqual(session['status'], 'started')
        self.assertIsNone(session['ended_at'])
        self.assertEqual(session['planned_duration_seconds'], 60)
        endpoint = '/api/sessions/' + session['id']
        end = self.end(session['id'])
        self.assertEqual(end.status_code, 200, end.text)
        self.assertEqual(end.json()['duration_seconds'], 60.012)
        self.assertEqual(self.end(session['id']).json(), end.json())
        feedback = self.client.put(endpoint + '/feedback', headers=self.headers, json={'feedback': 'helpful'})
        self.assertEqual(feedback.json()['feedback'], 'helpful')
        self.assertEqual(self.client.post('/api/sessions', headers=self.headers, json=payload).json()['status'], 'completed')
        self.assertEqual(self.end(session['id']).json()['feedback'], 'helpful')
        self.assertEqual(self.client.put(endpoint + '/feedback', headers=self.headers, json={'feedback':'helpful'}).json(), feedback.json())
        with closing(sqlite3.connect(self.path)) as connection:
            self.assertEqual(connection.execute('SELECT count(*) FROM exercise_sessions').fetchone(), (1,))

    def test_exiting_updates_existing_and_cannot_be_changed_to_completed(self):
        _, session = self.start('stop')
        body = self.end_body('exited', 2.345)
        self.assertEqual(self.end(session['id'], body).json()['status'], 'exited')
        self.assertEqual(self.end(session['id'], body).status_code, 200)
        self.assertEqual(self.end(session['id']).status_code, 409)
        self.assertEqual(self.client.put('/api/sessions/'+session['id']+'/feedback', headers=self.headers, json={'feedback':'skipped'}).status_code,409)

    def test_completed_status_end_and_duration_are_immutable(self):
        _, session = self.start()
        self.assertEqual(self.end(session['id']).status_code, 200)
        for body in [self.end_body('exited'), self.end_body(duration=61)]:
            self.assertEqual(self.end(session['id'], body).status_code, 409)

    def test_feedback_is_scoped_to_correct_session_and_intentional_changes(self):
        _, a = self.start('stop')
        _, b = self.start('stop')
        self.end(a['id'])
        self.end(b['id'])
        for value in ['helpful','not_helpful','skipped']:
            r=self.client.put('/api/sessions/'+a['id']+'/feedback',headers=self.headers,json={'feedback':value})
            self.assertEqual(r.json()['feedback'],value)
        self.assertIsNone(self.client.get('/api/sessions/'+b['id'],headers=self.headers).json()['feedback'])
        self.assertEqual(self.client.get('/api/sessions/'+a['id'],headers={'X-App-ID':str(uuid4())}).status_code,404)
        self.assertEqual(self.client.put('/api/sessions/'+b['id']+'/feedback',headers={'X-App-ID':str(uuid4())},json={'feedback':'helpful'}).status_code,404)

    def test_rejects_incomplete_breathing_bad_timestamps_and_duration(self):
        _, session = self.start()
        self.assertEqual(self.end(session['id'],self.end_body(duration=59.999)).status_code,422)
        self.assertEqual(self.end(session['id'],self.end_body('exited',-1)).status_code,422)
        body=self.end_body('exited',3)
        body['duration_seconds']=7
        self.assertEqual(self.end(session['id'],body).status_code,422)
        self.assertEqual(self.client.get('/api/sessions/'+session['id'],headers=self.headers).json()['status'],'started')

    def test_manual_stop_allows_short_or_long_duration_without_deadline(self):
        for seconds in [0.5, 125.5]:
            _, session = self.start('stop')
            self.assertEqual(self.end(session['id'],self.end_body(duration=seconds)).status_code,200)

    def test_daily_mood_first_wins_scoped_and_no_duplicates(self):
        endpoint='/api/mood-checkins/2026-10-19'
        first=self.client.put(endpoint,headers=self.headers,json={'mood':'okay'})
        self.assertEqual(first.status_code,200)
        self.assertEqual(self.client.put(endpoint,headers=self.headers,json={'mood':'okay'}).json(),first.json())
        self.assertEqual(self.client.put(endpoint,headers=self.headers,json={'mood':'calm'}).status_code,409)
        other=self.client.put(endpoint,headers={'X-App-ID':str(uuid4())},json={'mood':'skipped'})
        self.assertEqual(other.status_code,200)
        with closing(sqlite3.connect(self.path)) as connection:
            self.assertEqual(connection.execute('SELECT count(*) FROM daily_mood_checkins').fetchone(),(2,))
        self.assertEqual(self.client.get(endpoint,headers=self.headers).json(),first.json())

    def test_sessions_and_mood_survive_new_application_instance(self):
        _, session=self.start('stop')
        self.end(session['id'])
        self.client.put('/api/mood-checkins/2026-10-19',headers=self.headers,json={'mood':'skipped'})
        with TestClient(create_app(self.settings)) as restarted:
            self.assertEqual(restarted.get('/api/sessions/'+session['id'],headers=self.headers).json()['status'],'completed')
            self.assertEqual(restarted.get('/api/mood-checkins/2026-10-19',headers=self.headers).json()['mood'],'skipped')

    def test_validation_scope_and_database_failure(self):
        self.assertEqual(self.client.post('/api/sessions',json={}).status_code,422)
        self.assertEqual(self.client.put('/api/mood-checkins/2026-02-30',headers=self.headers,json={'mood':'calm'}).status_code,422)
        self.assertEqual(self.client.put('/api/mood-checkins/2026-10-19',headers=self.headers,json={'mood':'diagnosed'}).status_code,422)
        self.assertEqual(self.client.get('/api/sessions/'+str(uuid4()),headers=self.headers).status_code,404)
        self.path.unlink()
        response=self.client.put('/api/mood-checkins/2026-10-19',headers=self.headers,json={'mood':'calm'})
        self.assertEqual(response.status_code,503)
        self.assertEqual(response.json(),{'detail':'Local data could not be saved or loaded.'})
        self.assertFalse(self.path.exists())

    def test_concurrent_duplicate_start_and_conflicting_terminal_requests(self):
        payload, session=self.start('stop')
        with ThreadPoolExecutor(max_workers=4) as pool:
            results=list(pool.map(lambda _: self.client.post('/api/sessions',headers=self.headers,json=payload).status_code,range(8)))
        self.assertEqual(results,[200]*8)
        with ThreadPoolExecutor(max_workers=2) as pool:
            results=list(pool.map(lambda status: self.end(session['id'],self.end_body(status,60)).status_code,['completed','exited']))
        self.assertEqual(sorted(results),[200,409])
        with closing(sqlite3.connect(self.path)) as connection:
            self.assertEqual(connection.execute('SELECT count(*) FROM exercise_sessions').fetchone(),(1,))

    def test_upgrade_preserves_old_metadata(self):
        old_path=self.path.parent/'old.sqlite3'
        with closing(sqlite3.connect(old_path)) as connection,connection:
            connection.execute('CREATE TABLE app_metadata (key TEXT PRIMARY KEY,value TEXT NOT NULL)')
            connection.execute("INSERT INTO app_metadata VALUES ('schema_version','1')")
            connection.execute("INSERT INTO app_metadata VALUES ('fictional','keep')")
        initialize_database(old_path)
        initialize_database(old_path)
        with closing(sqlite3.connect(old_path)) as connection:
            self.assertEqual(connection.execute("SELECT value FROM app_metadata WHERE key='fictional'").fetchone(),('keep',))
            self.assertEqual(connection.execute("SELECT value FROM app_metadata WHERE key='schema_version'").fetchone(),('7',))
