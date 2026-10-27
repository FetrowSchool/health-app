from contextlib import closing
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sqlite3
import tempfile
import unittest
from uuid import uuid4

from fastapi.testclient import TestClient
from backend.app.config import Settings
from backend.app.database import initialize_database
from backend.app.main import create_app
from backend.app.feedback_policy import predefined_message


class GroundingTests(unittest.TestCase):
    def setUp(self):
        folder=tempfile.TemporaryDirectory(); self.addCleanup(folder.cleanup)
        self.path=Path(folder.name)/'app.sqlite3'
        self.settings=Settings(database_path=self.path) # deterministic mock, never local live settings
        self.client=self.enterContext(TestClient(create_app(self.settings)))
        self.headers={'X-App-ID':str(uuid4())}
        self.start=datetime(2026,10,19,12,tzinfo=timezone.utc)

    def create(self):
        body={'id':str(uuid4()),'exercise_type':'grounding_54321','started_at':self.start.isoformat(),'entry_duration_seconds':0.012}
        result=self.client.post('/api/sessions',headers=self.headers,json=body)
        self.assertEqual(result.status_code,200,result.text)
        self.assertEqual(result.json()['planned_duration_seconds'],70)
        self.assertEqual(self.client.post('/api/sessions',headers=self.headers,json=body).json(),result.json())
        return body['id']

    def end(self,id,status,duration):
        body={'status':status,'duration_seconds':duration,'ended_at':(self.start+timedelta(seconds=duration)).isoformat()}
        result=self.client.patch('/api/sessions/'+id,headers=self.headers,json=body)
        self.assertEqual(result.status_code,200,result.text)
        self.assertEqual(self.client.patch('/api/sessions/'+id,headers=self.headers,json=body).json(),result.json())
        return result.json()

    def test_grounding_complete_mock_feedback_order_duplicates_and_restart(self):
        id=self.create(); ended=self.end(id,'completed',70.125)
        self.assertEqual(ended['exercise_type'],'grounding_54321')
        for feedback in ['helpful','not_helpful']:
            self.assertEqual(self.client.put('/api/sessions/'+id+'/feedback',headers=self.headers,json={'feedback':feedback}).status_code,200)
            body={'request_id':str(uuid4()),'session_id':id,'exercise_type':'grounding_54321','feedback':feedback,'user_message':predefined_message('grounding_54321',feedback)}
            self.assertIn('5-4-3-2-1 Grounding',body['user_message'])
            response=self.client.post('/api/feedback-response',headers=self.headers,json=body)
            self.assertEqual(response.status_code,200,response.text)
            record=response.json();self.assertEqual(record['status'],'succeeded'); self.assertEqual(record['provider_mode'],'mock')
            self.assertEqual([m['role'] for m in record['messages']],['user','assistant'])
            self.assertEqual(record['session_id'],id)
            body['request_id']=str(uuid4())
            self.assertEqual(self.client.post('/api/feedback-response',headers=self.headers,json=body).json(),record)
        with TestClient(create_app(self.settings)) as restarted:
            self.assertEqual(restarted.get('/api/conversations/'+record['id'],headers=self.headers).json(),record)
        with closing(sqlite3.connect(self.path)) as c:
            self.assertEqual(c.execute('select count(*) from exercise_sessions').fetchone()[0],1)
            self.assertEqual(c.execute('select count(*) from conversations').fetchone()[0],2)
            self.assertEqual(c.execute('select count(*) from messages').fetchone()[0],4)

    def test_grounding_exit_and_optional_skipped_steps_have_no_minimum_or_deadline(self):
        for status,duration in [('exited',0.2),('completed',2),('completed',120)]:
            id=self.create(); record=self.end(id,status,duration)
            self.assertEqual(record['status'],status)
            self.assertEqual(record['duration_seconds'],duration)
        # A voluntary pause >90 seconds is recorded honestly, never forced out.
        self.assertEqual(self.client.get('/api/sessions/'+id,headers=self.headers).json()['duration_seconds'],120)


class GroundingMigrationTests(unittest.TestCase):
    def test_v3_history_and_relationships_preserved_repeated_migration(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'old.sqlite3'
            with closing(sqlite3.connect(path)) as c,c:
                c.executescript((Path(__file__).parent/'fixtures/schema-v3.sql').read_text())
                c.execute("insert into app_metadata values ('schema_version','3')")
                c.execute("insert into app_metadata values ('fictional_note','preserve')")
                c.execute("insert into exercise_sessions values ('s','a','stop','2026-10-19T12:00:00+00:00','2026-10-19T12:01:00+00:00','completed',60,0.01,60,'helpful')")
                c.execute("insert into conversations values ('c','a','s','stop','helpful','2026-10-19T12:01:01+00:00','mock','succeeded',NULL)")
                c.execute("insert into messages values ('m','c',1,'user','Fictional historic button message','2026-10-19T12:01:01+00:00')")
                c.execute("insert into daily_mood_checkins values ('a','2026-10-19','okay','2026-10-19T12:00:00+00:00')")
                tables=['exercise_sessions','conversations','messages','daily_mood_checkins']
                columns={t:[r[1] for r in c.execute('pragma table_info('+t+')')] for t in tables}
                before={t:c.execute('select * from '+t).fetchall() for t in tables}
            for _ in range(2):initialize_database(path)
            with closing(sqlite3.connect(path)) as c:
                for t in tables:self.assertEqual(c.execute('select '+','.join(columns[t])+' from '+t).fetchall(),before[t])
                self.assertEqual(c.execute('pragma foreign_key_check').fetchall(),[])
                self.assertEqual(c.execute("select value from app_metadata where key='schema_version'").fetchone(),('7',))
                self.assertEqual(c.execute("select value from app_metadata where key='fictional_note'").fetchone(),('preserve',))
                c.execute("insert into exercise_sessions (id,app_id,exercise_type,started_at,entry_duration_seconds,planned_duration_seconds) values ('g','a','grounding_54321','2026-10-19T12:00:00+00:00',0,70)")
                with self.assertRaises(sqlite3.IntegrityError):
                    c.execute("insert into exercise_sessions (id,app_id,exercise_type,started_at,entry_duration_seconds,planned_duration_seconds) values ('bad','a','grounding_54321','2026-10-19T12:00:00+00:00',0,60)")

    def test_invalid_legacy_relationship_rolls_back_migration(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'old.sqlite3'
            with closing(sqlite3.connect(path)) as c,c:
                c.executescript((Path(__file__).parent/'fixtures/schema-v3.sql').read_text())
                c.execute("insert into app_metadata values ('schema_version','3')")
                c.execute("insert into messages values ('orphan','missing',1,'user','Fictional','2026-10-19T12:00:00+00:00')")
                old=c.execute("select sql from sqlite_master where name='exercise_sessions'").fetchone()
            with self.assertRaisesRegex(RuntimeError,'relationships'):initialize_database(path)
            with closing(sqlite3.connect(path)) as c:
                self.assertEqual(c.execute("select value from app_metadata").fetchone(),('3',))
                self.assertEqual(c.execute("select sql from sqlite_master where name='exercise_sessions'").fetchone(),old)
                self.assertEqual(c.execute('select count(*) from messages').fetchone(),(1,))
