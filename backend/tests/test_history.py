from contextlib import closing
from datetime import datetime, timedelta, timezone
from pathlib import Path
import json
import sqlite3
import tempfile
import unittest
from uuid import UUID, uuid4
from fastapi.testclient import TestClient
from backend.app.config import Settings
from backend.app.main import create_app
from backend.app.activity_controller import transaction


class HistoryTests(unittest.TestCase):
    def setUp(self):
        folder=tempfile.TemporaryDirectory();self.addCleanup(folder.cleanup)
        self.path=Path(folder.name)/'history.sqlite3'
        self.settings=Settings(database_path=self.path)
        self.client=self.enterContext(TestClient(create_app(self.settings)))
        self.identity=str(uuid4());self.headers={'X-App-ID':self.identity}
        self.base=datetime(2026,11,1,12,tzinfo=timezone.utc)

    def session(self,index=0,status='completed',exercise='paced_breathing',owner=None,duration=60):
        id=str(uuid4());start=self.base+timedelta(minutes=index)
        with closing(sqlite3.connect(self.path)) as c,c:
            c.execute('insert into exercise_sessions (id,app_id,exercise_type,started_at,ended_at,status,duration_seconds,entry_duration_seconds,planned_duration_seconds,feedback) values (?,?,?,?,?,?,?,?,?,?)',
                (id,owner or self.identity,exercise,start.isoformat(),None if status=='started' else (start+timedelta(seconds=duration)).isoformat(),status,0 if status=='started' else duration,0,70 if exercise=='grounding_54321' else 60,'helpful' if status=='completed' else None))
        return id

    def conversation(self,index=0,owner=None,status='succeeded',kind='feedback'):
        id=str(uuid4());now=(self.base+timedelta(minutes=index)).isoformat()
        session=self.session(index,owner=owner) if kind=='feedback' else None
        content=json.dumps({'exercise_id':'paced_breathing','short_reason':'Paced Breathing offers a steady rhythm to follow.'}) if kind=='recommendation' else 'Fictional saved assistant response.'
        with closing(sqlite3.connect(self.path)) as c,c:
            c.execute('insert into conversations (id,app_id,session_id,exercise_type,feedback,created_at,provider_mode,status,failure_code,kind,focus,context_json) values (?,?,?,?,?,?,?,?,?,?,?,?)',
                (id,owner or self.identity,session,'paced_breathing' if session else None,'helpful' if session else None,now,'mock',status,'provider_error' if status=='failed' else None,kind,'not_sure' if kind=='recommendation' else None,'{"mood":"anxious","recent":[]}'))
            # Reverse insertion order to prove saved ordinal/chronological retrieval.
            if status=='succeeded':c.execute('insert into messages values (?,?,?,?,?,?)',(str(uuid4()),id,2,'assistant',content,(self.base+timedelta(minutes=index,seconds=1)).isoformat()))
            c.execute('insert into messages values (?,?,?,?,?,?)',(str(uuid4()),id,1,'user','Fictional private text absent from previews.',now))
        return id

    def read(self,query=''):
        return self.client.get('/api/history'+query,headers=self.headers)

    def test_empty_and_projected_scope_newest_first_bound_no_private_previews(self):
        self.assertEqual(self.read().json(),dict(sessions=[],conversations=[],recent_completed_exercise=None))
        first=self.conversation(0);latest=self.conversation(2,kind='recommendation')
        self.conversation(5,owner=str(uuid4()));self.session(8,status='exited')
        result=self.read('?limit=2');self.assertEqual(result.status_code,200,result.text)
        self.assertEqual(result.headers['cache-control'],'no-store')
        body=result.json();self.assertEqual(len(body['sessions']),2)
        self.assertEqual([c['id'] for c in body['conversations']],[latest,first])
        self.assertEqual(body['sessions'][0]['status'],'exited')
        encoded=json.dumps(body)
        for forbidden in ['Fictional private','Fictional saved assistant','context_used','context_json','anxious','app_id','messages','instructions','api_key']:
            self.assertNotIn(forbidden,encoded)

    def test_personalization_uses_latest_completion_not_last_entry_exit_or_other_owner(self):
        self.session(0,duration=900)  # Ends after the later-starting grounding session.
        self.session(1,exercise='grounding_54321',duration=70)
        self.session(20,status='exited');self.session(21,status='started')
        self.session(30,exercise='stop');self.session(40,owner=str(uuid4()),exercise='grounding_54321')
        self.assertEqual(self.read('?limit=1').json()['recent_completed_exercise'],'paced_breathing')

    def test_durations_started_and_new_active_summary_are_truthful(self):
        id=self.session(0,duration=95.881);self.session(2,status='started')
        with closing(sqlite3.connect(self.path)) as c,c:
            c.execute('update exercise_sessions set active_duration_seconds=66.147,optional_continuation_seconds=6.147,active_completed_cycles=6 where id=?',(id,))
        rows=self.read().json()['sessions']
        self.assertIsNone(rows[0]['duration_seconds']);self.assertEqual(rows[0]['status'],'started')
        self.assertEqual(rows[1]['duration_seconds'],95.881);self.assertEqual(rows[1]['active_duration_seconds'],66.147)
        self.assertEqual(rows[1]['feedback'],'helpful')

    def test_failed_pending_and_historical_messages_keep_saved_order_and_scope(self):
        historical=self.conversation(kind='recommendation')
        failed=self.conversation(1,status='failed');self.conversation(2,status='pending')
        summaries=self.read().json()['conversations']
        self.assertEqual([c['status'] for c in summaries],['pending','failed','succeeded'])
        endpoint='/api/conversations/'+historical
        record=self.client.get(endpoint,headers=self.headers).json()
        self.assertEqual([m['ordinal'] for m in record['messages']],[1,2])
        self.assertLess(record['messages'][0]['created_at'],record['messages'][1]['created_at'])
        self.assertEqual(len(self.client.get('/api/conversations/'+failed,headers=self.headers).json()['messages']),1)
        self.assertEqual(self.client.get(endpoint,headers={'X-App-ID':str(uuid4())}).status_code,404)
        self.assertEqual(self.client.get('/api/conversations/not-a-uuid',headers=self.headers).status_code,422)
        self.assertEqual(self.client.get('/api/conversations/'+str(uuid4()),headers=self.headers).status_code,404)

    def test_limits_identity_missing_database_are_validated_sanitized(self):
        for value in ['0','51','-1','abc','1.5']:
            self.assertEqual(self.read('?limit='+value).status_code,422)
        self.assertEqual(self.client.get('/api/history').status_code,422)
        self.assertEqual(self.client.get('/api/history',headers={'X-App-ID':'invalid'}).status_code,422)
        self.path.unlink();result=self.read()
        self.assertEqual(result.status_code,503);self.assertNotIn(str(self.path),result.text)
        self.assertFalse(self.path.exists())

    def test_reads_and_restart_preserve_every_row_and_read_connection_rejects_write(self):
        id=self.conversation();self.conversation(1,kind='recommendation')
        tables=['app_metadata','exercise_sessions','daily_mood_checkins','conversations','messages']
        with closing(sqlite3.connect(self.path)) as c:before={t:c.execute('select * from '+t).fetchall() for t in tables}
        expected=self.read().json()
        with transaction(self.path,write=False) as connection:
            with self.assertRaises(sqlite3.OperationalError):connection.execute("delete from messages")
        with TestClient(create_app(self.settings)) as restarted:
            self.assertEqual(restarted.get('/api/history',headers=self.headers).json(),expected)
            self.assertEqual(restarted.get('/api/conversations/'+id,headers=self.headers).status_code,200)
        with closing(sqlite3.connect(self.path)) as c:
            for t,rows in before.items():self.assertEqual(c.execute('select * from '+t).fetchall(),rows)
            self.assertEqual(c.execute('pragma foreign_key_check').fetchall(),[])
