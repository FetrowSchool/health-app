"""Retired creation route, historical reads and shared feedback remain compatible."""
import asyncio
from contextlib import closing
from datetime import datetime, timedelta, timezone
from pathlib import Path
import json
import sqlite3
import tempfile
import unittest
from uuid import uuid4
import httpx
from fastapi.testclient import TestClient
from backend.app.config import Settings
from backend.app.main import create_app
from backend.app.database import initialize_database
from backend.app.feedback_policy import FeedbackContext, predefined_message
from backend.app.providers import LiveProvider, MockProvider


class RecordingProvider(MockProvider):
    def __init__(self): self.calls=[]
    async def generate(self, context):
        self.calls.append(context)
        return await super().generate(context)


class ConversationCompatibilityTests(unittest.TestCase):
    def setUp(self):
        folder=tempfile.TemporaryDirectory(); self.addCleanup(folder.cleanup)
        self.path=Path(folder.name)/'app.sqlite3'; self.settings=Settings(database_path=self.path)
        self.provider=RecordingProvider()
        self.client=self.enterContext(TestClient(create_app(self.settings,self.provider)))
        self.app_id=str(uuid4()); self.headers={'X-App-ID':self.app_id}
        self.start=datetime(2026,10,26,12,tzinfo=timezone.utc)

    def session(self, exercise='grounding_54321', index=0, headers=None):
        headers=headers or self.headers; id=str(uuid4()); start=self.start+timedelta(minutes=index)
        result=self.client.post('/api/sessions',headers=headers,json=dict(id=id,exercise_type=exercise,started_at=start.isoformat(),entry_duration_seconds=0))
        self.assertEqual(result.status_code,200)
        result=self.client.patch('/api/sessions/'+id,headers=headers,json=dict(status='completed',ended_at=(start+timedelta(seconds=70)).isoformat(),duration_seconds=70))
        self.assertEqual(result.status_code,200)
        return id

    def test_retired_creation_route_is_absent_and_cannot_write_or_generate(self):
        self.assertNotIn('/api/recommendations',self.client.get('/openapi.json').json()['paths'])
        result=self.client.post('/api/recommendations',headers=self.headers,json=dict(request_id=str(uuid4()),focus='not_sure',local_date='2026-10-26'))
        self.assertEqual(result.status_code,404);self.assertEqual(self.provider.calls,[])
        with closing(sqlite3.connect(self.path)) as c:
            self.assertEqual(c.execute('select count(*) from conversations').fetchone(),(0,))
            self.assertEqual(c.execute('select count(*) from messages').fetchone(),(0,))

    def test_historical_recommendation_remains_scoped_readable_and_unchanged_after_restart(self):
        id=str(uuid4()); now=self.start.isoformat()
        historical={'exercise_id':'grounding_54321','short_reason':'Grounding focuses on one sense at a time.'}
        with closing(sqlite3.connect(self.path)) as c,c:
            c.execute("insert into conversations (id,app_id,created_at,provider_mode,status,kind,focus,context_json) values (?,?,?,'mock','succeeded','recommendation','surroundings','{}')",(id,self.app_id,now))
            c.execute('insert into messages values (?,?,?,?,?,?)',(str(uuid4()),id,1,'user','Fictional historical focus choice.',now))
            c.execute('insert into messages values (?,?,?,?,?,?)',(str(uuid4()),id,2,'assistant',json.dumps(historical),now))
            before={t:c.execute('select * from '+t).fetchall() for t in ['conversations','messages']}
        endpoint='/api/conversations/'+id
        result=self.client.get(endpoint,headers=self.headers)
        self.assertEqual(result.status_code,200); row=result.json()
        self.assertEqual(row['recommendation'],historical)
        self.assertEqual([m['role'] for m in row['messages']],['user','assistant'])
        self.assertEqual(self.client.get(endpoint,headers={'X-App-ID':str(uuid4())}).status_code,404)
        with TestClient(create_app(self.settings)) as restarted:
            self.assertEqual(restarted.get(endpoint,headers=self.headers).json(),row)
        with closing(sqlite3.connect(self.path)) as c:
            for t,rows in before.items():self.assertEqual(c.execute('select * from '+t).fetchall(),rows)
            self.assertEqual(c.execute('pragma foreign_key_check').fetchall(),[])
        self.assertEqual(self.provider.calls,[])

    def test_shared_feedback_keeps_bounded_scoped_context_and_other_exercise_copy(self):
        self.client.put('/api/mood-checkins/2026-10-26',headers=self.headers,json={'mood':'okay'})
        other={'X-App-ID':str(uuid4())}
        self.client.put('/api/mood-checkins/2026-10-26',headers=other,json={'mood':'overwhelmed'})
        for n in range(5):id=self.session('paced_breathing' if n%2 else 'grounding_54321',n)
        self.session('stop',6);self.session(index=7,headers=other)
        result=self.client.post('/api/feedback-response',headers=self.headers,json=dict(request_id=str(uuid4()),session_id=id,exercise_type='grounding_54321',feedback='not_helpful',local_date='2026-10-26',user_message=predefined_message('grounding_54321','not_helpful')))
        self.assertEqual(result.status_code,200,result.text)
        self.assertEqual(result.json()['status'],'succeeded')
        self.assertIn('Paced Breathing',result.json()['messages'][1]['content'])
        context=self.provider.calls[0]
        self.assertEqual(context.mood,'okay');self.assertEqual(len(context.recent),3)
        self.assertEqual(set(context.recent[0]),{'exercise_type','status','feedback'})
        self.assertNotIn(self.app_id,repr(context));self.assertNotIn('stop',repr(context.recent))

    def test_shared_live_feedback_adapter_keeps_its_mocked_http_contract(self):
        captured=[]
        def handler(request):
            captured.append(json.loads(request.content))
            return httpx.Response(200,json={'choices':[{'message':{'content':'Feedback noted. You can choose what to do next.'}}]})
        provider=LiveProvider(Settings(model_api_key='synthetic',model_name='synthetic-model',model_endpoint='https://openrouter.ai/api/v1/chat/completions'),httpx.MockTransport(handler))
        context=FeedbackContext('grounding_54321','helpful',predefined_message('grounding_54321','helpful'),'okay',())
        text=asyncio.run(provider.generate(context))
        self.assertEqual(text,'Feedback noted. You can choose what to do next.')
        self.assertEqual(captured[0]['max_tokens'],80)
        self.assertEqual(captured[0]['reasoning'],{'enabled':False})
        self.assertIn('"mood": "okay"',captured[0]['messages'][1]['content'])
        self.assertNotIn('focus',captured[0]['messages'][1]['content'])

    def test_v4_migration_preserves_every_old_field_and_relationship(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'v4.sqlite3'
            with closing(sqlite3.connect(path)) as c,c:
                c.executescript((Path(__file__).parent/'fixtures/schema-v4.sql').read_text())
                c.execute("insert into app_metadata values ('schema_version','4')")
                c.execute("insert into exercise_sessions values ('s','a','grounding_54321','2026-10-19T12:00:00+00:00','2026-10-19T12:01:10+00:00','completed',70,0,70,'helpful')")
                c.execute("insert into conversations values ('c','a','s','grounding_54321','helpful','2026-10-19T12:01:11+00:00','mock','succeeded',NULL)")
                c.execute("insert into messages values ('m','c',1,'user','Fictional','2026-10-19T12:01:11+00:00')")
                before={t:([r[1] for r in c.execute('pragma table_info('+t+')')],c.execute('select * from '+t).fetchall()) for t in ['exercise_sessions','conversations','messages','daily_mood_checkins']}
            initialize_database(path);initialize_database(path)
            with closing(sqlite3.connect(path)) as c:
                for t,(cols,rows) in before.items():self.assertEqual(c.execute('select '+','.join(cols)+' from '+t).fetchall(),rows)
                self.assertEqual(c.execute('select kind,focus,context_json from conversations').fetchone(),('feedback',None,'{}'))
                self.assertEqual(c.execute('pragma foreign_key_check').fetchall(),[])
                self.assertEqual(c.execute("select value from app_metadata where key='schema_version'").fetchone(),('7',))
