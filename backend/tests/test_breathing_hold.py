"""Fictional hold/pause session timing and additive schema compatibility."""
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


class HoldBreathingTests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.path = Path(folder.name) / 'hold.sqlite3'
        self.settings = Settings(database_path=self.path)
        self.client = self.enterContext(TestClient(create_app(self.settings)))
        self.headers = {'X-App-ID': str(uuid4())}
        self.started = datetime(2026, 10, 26, 12, tzinfo=timezone.utc)

    def start(self, exercise='paced_breathing'):
        payload = dict(id=str(uuid4()), exercise_type=exercise,
                       started_at=self.started.isoformat(), entry_duration_seconds=2.5)
        result = self.client.post('/api/sessions', headers=self.headers, json=payload)
        self.assertEqual(result.status_code, 200, result.text)
        return payload

    def body(self, active=2.5, wall=12.5, status='completed'):
        return dict(status=status, ended_at=(self.started + timedelta(seconds=wall)).isoformat(),
                    duration_seconds=wall, active_duration_seconds=active,
                    optional_continuation_seconds=max(0, active - 60), active_completed_cycles=int(active // 10))

    def end(self, payload, body):
        return self.client.patch('/api/sessions/' + payload['id'], headers=self.headers, json=body)

    def test_early_finish_pauses_one_record_feedback_and_restart(self):
        payload = self.start()
        result = self.end(payload, self.body())
        self.assertEqual(result.status_code, 200, result.text)
        row = result.json()
        self.assertEqual((row['status'], row['planned_duration_seconds'], row['active_duration_seconds'], row['duration_seconds']), ('completed', 60, 2.5, 12.5))
        self.assertIsNone(row['interaction_mode'])
        self.assertEqual(self.end(payload, self.body()).json(), row)
        self.assertEqual(self.client.post('/api/sessions', headers=self.headers, json=payload).status_code, 200)
        endpoint = '/api/sessions/' + payload['id']
        feedback = self.client.put(endpoint + '/feedback', headers=self.headers, json={'feedback':'skipped'})
        self.assertEqual(feedback.status_code, 200)
        with TestClient(create_app(self.settings)) as restarted:
            self.assertEqual(restarted.get(endpoint, headers=self.headers).json(), feedback.json())
        with closing(sqlite3.connect(self.path)) as c:
            self.assertEqual(c.execute('select count(*) from exercise_sessions').fetchone(), (1,))

    def test_optional_continuation_has_uncapped_cycles_and_exit_is_distinct(self):
        for status in ['completed', 'exited']:
            payload = self.start()
            result = self.end(payload, self.body(active=95.75, wall=110.5, status=status))
            self.assertEqual(result.status_code, 200, result.text)
            row = result.json()
            self.assertEqual((row['status'], row['active_completed_cycles'], row['optional_continuation_seconds']), (status, 9, 35.75))
            self.assertEqual(self.end(payload, self.body(active=95.5, wall=110.5, status=status)).status_code, 409)
            if status == 'exited':
                self.assertEqual(self.client.put('/api/sessions/' + payload['id'] + '/feedback', headers=self.headers, json={'feedback':'skipped'}).status_code, 409)

    def test_partial_inconsistent_wrong_skill_and_nonfinite_summaries_reject(self):
        body = self.body()
        invalid = [{k:v for k,v in body.items() if k != 'active_completed_cycles'},
                   {**body, 'active_duration_seconds':13}, {**body, 'optional_continuation_seconds':1},
                   {**body, 'active_completed_cycles':1}, {**body, 'active_completed_cycles':True},
                   {**body, 'active_duration_seconds':-1}, {**body, 'active_duration_seconds':'NaN'},
                   {**body, 'interaction_mode':'hold', 'inhale_interactions':1, 'exhale_interactions':0, 'completed_cycles':0}]
        payload = self.start()
        for value in invalid:
            self.assertEqual(self.end(payload, value).status_code, 422, value)
        for exercise in ['grounding_54321', 'stop']:
            self.assertEqual(self.end(self.start(exercise), body).status_code, 422)

    def test_v6_migration_preserves_legacy_values_and_related_records(self):
        payload = self.start()
        legacy = dict(status='completed', ended_at=(self.started + timedelta(seconds=60)).isoformat(), duration_seconds=60,
                      interaction_mode='hold', inhale_interactions=4, exhale_interactions=6, completed_cycles=6)
        self.assertEqual(self.end(payload, legacy).status_code, 200)
        with closing(sqlite3.connect(self.path)) as c, c:
            for column in ['active_duration_seconds', 'optional_continuation_seconds', 'active_completed_cycles']:
                c.execute('alter table exercise_sessions drop column ' + column)
            c.execute("update app_metadata set value='6' where key='schema_version'")
            originals = {}
            for table in ['exercise_sessions', 'daily_mood_checkins', 'conversations', 'messages']:
                columns = [r[1] for r in c.execute('pragma table_info(' + table + ')')]
                originals[table] = (columns, c.execute('select * from ' + table).fetchall())
        initialize_database(self.path)
        initialize_database(self.path)
        with closing(sqlite3.connect(self.path)) as c:
            for table, (columns, rows) in originals.items():
                self.assertEqual(c.execute('select ' + ','.join(columns) + ' from ' + table).fetchall(), rows)
            self.assertEqual(c.execute('select active_duration_seconds,optional_continuation_seconds,active_completed_cycles from exercise_sessions').fetchone(), (None,None,None))
            self.assertEqual(c.execute("select value from app_metadata where key='schema_version'").fetchone(), ('7',))
            self.assertEqual(c.execute('pragma foreign_key_check').fetchall(), [])
