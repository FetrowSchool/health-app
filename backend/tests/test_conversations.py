import asyncio
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
import json
import sqlite3
import tempfile
import threading
import time
import unittest
from unittest.mock import patch
from uuid import uuid4

import httpx
from fastapi import HTTPException
from fastapi.testclient import TestClient
from backend.app.config import Settings
from backend.app.main import create_app
from backend.app.feedback_policy import APPROVED_RESPONSES, FALLBACK, FeedbackContext, predefined_message
from backend.app.providers import LiveProvider, ProviderFailure


class StubProvider:
    mode = 'mock'
    def __init__(self, output=None, error=None, delay=0):
        self.output, self.error, self.delay = output, error, delay
        self.calls = []
        self.started = threading.Event()
    async def generate(self, context):
        self.calls.append(context)
        self.started.set()
        await asyncio.sleep(self.delay)
        if self.error: raise self.error
        return APPROVED_RESPONSES[context.feedback] if self.output is None else self.output


class ConversationTests(unittest.TestCase):
    def setUp(self):
        folder=tempfile.TemporaryDirectory();self.addCleanup(folder.cleanup)
        self.path=Path(folder.name)/'app.sqlite3'
        self.settings=Settings(database_path=self.path,provider_timeout_seconds=0.2)
        self.provider=StubProvider()
        self.app=create_app(self.settings,self.provider)
        self.client=self.enterContext(TestClient(self.app))
        self.headers={'X-App-ID':str(uuid4())}
        self.start=datetime(2026,10,19,12,tzinfo=timezone.utc)
        self.session_id=self.create_session()

    def create_session(self, completed=True):
        id=str(uuid4())
        self.assertEqual(self.client.post('/api/sessions',headers=self.headers,json={
            'id':id,'exercise_type':'stop','started_at':self.start.isoformat(),'entry_duration_seconds':0.01
        }).status_code,200)
        if completed:
            self.assertEqual(self.client.patch('/api/sessions/'+id,headers=self.headers,json={
                'status':'completed','ended_at':(self.start+timedelta(seconds=60)).isoformat(),'duration_seconds':60
            }).status_code,200)
        return id

    def body(self, feedback='helpful', session_id=None):
        return dict(request_id=str(uuid4()),session_id=session_id or self.session_id,
                    exercise_type='stop',feedback=feedback,user_message=predefined_message('stop',feedback))

    def post(self, body=None):
        return self.client.post('/api/feedback-response',headers=self.headers,json=body or self.body())

    def test_helpful_and_not_helpful_have_scoped_ordered_saved_messages(self):
        for feedback in ['helpful','not_helpful']:
            r=self.post(self.body(feedback));self.assertEqual(r.status_code,200,r.text)
            record=r.json();self.assertEqual(record['status'],'succeeded')
            self.assertTrue(record['saved']);self.assertEqual(record['provider_mode'],'mock')
            self.assertEqual(record['session_id'],self.session_id)
            self.assertEqual([m['role'] for m in record['messages']],['user','assistant'])
            self.assertEqual([m['ordinal'] for m in record['messages']],[1,2])
            self.assertEqual(record['messages'][1]['content'],APPROVED_RESPONSES[feedback])
            self.assertIsNone(record['fallback_message'])
            self.assertEqual(self.client.get('/api/conversations/'+record['id'],headers=self.headers).json(),record)
            self.assertEqual(self.client.get('/api/conversations/'+record['id'],headers={'X-App-ID':str(uuid4())}).status_code,404)
        self.assertEqual(len(self.provider.calls),2)
        self.assertEqual(set(vars(self.provider.calls[0])),{'exercise_type','feedback','user_message','mood','recent'})

    def test_repeated_ids_and_new_ids_same_button_deduplicate(self):
        body=self.body();first=self.post(body).json()
        self.assertEqual(self.post(body).json(),first)
        self.assertEqual(self.post(self.body()).json(),first)
        self.assertEqual(len(self.provider.calls),1)
        with closing(sqlite3.connect(self.path)) as c:
            self.assertEqual(c.execute('SELECT count(*) FROM conversations').fetchone(),(1,))
            self.assertEqual(c.execute('SELECT count(*) FROM messages').fetchone(),(2,))
        changed={**self.body('not_helpful'),'request_id':body['request_id']}
        self.assertEqual(self.post(changed).status_code,409)

    def test_rejects_free_text_crisis_scenarios_skip_and_wrong_context_without_provider(self):
        body=self.body()
        for invalid in [{**body,'user_message':'Fictional crisis-related disclosure, not a button selection.'},
                        {**body,'feedback':'skipped'},{**body,'exercise_type':'paced_breathing'},
                        {**body,'mood':'overwhelmed'}]:
            self.assertEqual(self.post(invalid).status_code,422)
        invalid={**body,'exercise_type':'paced_breathing','user_message':predefined_message('paced_breathing','helpful')}
        self.assertEqual(self.post(invalid).status_code,409)
        self.assertEqual(self.client.post('/api/feedback-response',headers={'X-App-ID':str(uuid4())},json=body).status_code,404)
        self.assertEqual(self.post(self.body(session_id=self.create_session(False))).status_code,409)
        self.assertEqual(len(self.provider.calls),0)
        with closing(sqlite3.connect(self.path)) as c:
            self.assertEqual(c.execute('SELECT count(*) FROM conversations').fetchone(),(0,))

    def assert_failure(self, response, code):
        self.assertEqual(response.status_code,200,response.text)
        record=response.json();self.assertEqual(record['status'],'failed')
        self.assertEqual(record['failure_code'],code)
        self.assertEqual(record['fallback_message'],FALLBACK)
        self.assertEqual([m['role'] for m in record['messages']],['user'])
        session=self.client.get('/api/sessions/'+self.session_id,headers=self.headers).json()
        self.assertEqual(session['status'],'completed')
        return record

    def test_timeout_is_bounded_failure_and_does_not_invent_assistant(self):
        self.provider.delay=1
        before=time.monotonic()
        record=self.assert_failure(self.post(),'provider_timeout')
        self.assertLess(time.monotonic()-before,0.8)
        self.assertEqual(self.post(self.body()).json(),record)
        self.assertEqual(len(self.provider.calls),1)

    def test_provider_error_does_not_leak_details(self):
        self.provider.error=RuntimeError('SYNTHETIC_PRIVATE_SENTINEL')
        response=self.post();self.assert_failure(response,'provider_error')
        self.assertNotIn('SYNTHETIC_PRIVATE_SENTINEL',response.text)
        with closing(sqlite3.connect(self.path)) as c:
            self.assertNotIn('SYNTHETIC_PRIVATE_SENTINEL',str(c.execute('SELECT * FROM conversations').fetchall()))

    def test_invalid_unsafe_or_action_outputs_are_not_displayed_or_persisted(self):
        for output in ['', 'You have a diagnosis.', '<script>navigate()</script>', {'navigate':'crisis'}, 'x'*1000]:
            self.provider.output=output
            record=self.assert_failure(self.post(self.body(session_id=self.create_session())),'invalid_response')
            self.assertEqual(len(record['messages']),1)
        with closing(sqlite3.connect(self.path)) as c:
            self.assertEqual(c.execute("SELECT count(*) FROM messages WHERE role='assistant'").fetchone(),(0,))

    def test_missing_live_credentials_is_explicit_failure_not_mock_success(self):
        with TestClient(create_app(replace(self.settings,model_provider='live'))) as client:
            response=client.post('/api/feedback-response',headers=self.headers,json=self.body())
        record=self.assert_failure(response,'missing_configuration')
        self.assertEqual(record['provider_mode'],'live')
        self.assertFalse(self.client.get('/api/health').json()['model_configured'])

    def test_restart_keeps_messages_order_and_marks_abandoned_pending_failed(self):
        saved=self.post().json()
        pending_id=str(uuid4())
        with closing(sqlite3.connect(self.path)) as c,c:
            c.execute("INSERT INTO conversations (id,app_id,session_id,exercise_type,feedback,created_at,provider_mode,status) VALUES (?,?,?,?,?,?,?,?)",
                      (pending_id,self.headers['X-App-ID'],self.session_id,'stop','not_helpful',self.start.isoformat(),'mock','pending'))
        with TestClient(create_app(self.settings)) as restarted:
            self.assertEqual(restarted.get('/api/conversations/'+saved['id'],headers=self.headers).json(),saved)
            abandoned=restarted.get('/api/conversations/'+pending_id,headers=self.headers).json()
            self.assertEqual(abandoned['failure_code'],'interrupted')
            self.assertEqual(abandoned['messages'],[])

    def test_concurrent_duplicate_responds_pending_and_calls_provider_once(self):
        self.provider.delay=0.1
        body=self.body()
        with ThreadPoolExecutor(max_workers=2) as pool:
            first=pool.submit(self.post,body)
            self.assertTrue(self.provider.started.wait(1))
            duplicate=self.post(body)
            self.assertEqual(duplicate.status_code,202)
            self.assertEqual(duplicate.json()['status'],'pending')
            self.assertEqual(first.result().json()['status'],'succeeded')
        self.assertEqual(len(self.provider.calls),1)
        self.assertEqual(len(self.post(body).json()['messages']),2)

    def test_database_failure_is_unsaved_and_never_returns_an_unstored_reply(self):
        with patch('backend.app.conversation_store.finalize',side_effect=HTTPException(503,'Local data could not be saved or loaded.')):
            response=self.post()
        self.assertEqual(response.status_code,503)
        self.assertNotIn(APPROVED_RESPONSES['helpful'],response.text)
        with closing(sqlite3.connect(self.path)) as c:
            self.assertEqual(c.execute("SELECT count(*) FROM messages WHERE role='assistant'").fetchone(),(0,))
            self.assertEqual(c.execute('SELECT status FROM exercise_sessions WHERE id=?',(self.session_id,)).fetchone(),('completed',))


class LiveAdapterTests(unittest.IsolatedAsyncioTestCase):
    async def test_mock_http_transport_sends_only_reviewed_context_and_no_tools(self):
        captured=[]
        def handler(request):
            captured.append(request)
            return httpx.Response(200,json={'choices':[{'message':{'content':APPROVED_RESPONSES['helpful']}}]})
        settings=Settings(model_provider='live',model_api_key='synthetic-test-key',model_name='fictional-test-model',model_endpoint='https://provider.example/chat/completions')
        provider=LiveProvider(settings,httpx.MockTransport(handler))
        response=await provider.generate(FeedbackContext('stop','helpful',predefined_message('stop','helpful')))
        self.assertEqual(response,APPROVED_RESPONSES['helpful'])
        body=json.loads(captured[0].content)
        self.assertEqual(set(body),{'model','messages','max_tokens','temperature'})
        self.assertNotIn('synthetic-test-key',captured[0].content.decode())
        self.assertNotIn('app_id',captured[0].content.decode())
        self.assertEqual(captured[0].headers['authorization'],'Bearer synthetic-test-key')

    async def test_mock_transport_rejects_http_errors_tools_and_malformed_results(self):
        cases=[(500,{},'provider_error'),(200,{'choices':[{'message':{'tool_calls':[{}]}}]},'invalid_response'),(200,{'choices':[]},'invalid_response')]
        for status,body,code in cases:
            transport=httpx.MockTransport(lambda request:httpx.Response(status,json=body))
            provider=LiveProvider(Settings(model_api_key='synthetic',model_name='test',model_endpoint='https://provider.example/chat/completions'),transport)
            with self.assertRaises(ProviderFailure) as error:
                await provider.generate(FeedbackContext('stop','helpful','fixed test message'))
            self.assertEqual(error.exception.code,code)


class OpenRouterCompatibilityTests(unittest.IsolatedAsyncioTestCase):
    async def test_openrouter_disables_reasoning_and_keeps_fixed_context(self):
        captured=[]
        def handler(request):
            captured.append(json.loads(request.content))
            return httpx.Response(200,json={'choices':[{'message':{'content':APPROVED_RESPONSES['not_helpful']}}]})
        settings=Settings(model_api_key='synthetic-test-key',model_name='fictional-model',
            model_endpoint='https://openrouter.ai/api/v1/chat/completions',provider_timeout_seconds=25)
        result=await LiveProvider(settings,httpx.MockTransport(handler)).generate(
            FeedbackContext('stop','not_helpful',predefined_message('stop','not_helpful')))
        self.assertEqual(result,APPROVED_RESPONSES['not_helpful'])
        self.assertEqual(captured[0]['reasoning'],{'enabled':False})
        self.assertEqual(captured[0]['max_tokens'],80)
        self.assertNotIn('tools',captured[0])

    def test_timeout_configuration_is_finite_and_bounded(self):
        from backend.app.config import load_settings
        for value in ['nan','inf','0','26','secret-invalid-value']:
            with patch('backend.app.config.load_dotenv'), patch.dict('os.environ',{'MODEL_TIMEOUT_SECONDS':value}):
                with self.assertRaisesRegex(ValueError,'between 1 and 25'):
                    load_settings()
        with patch('backend.app.config.load_dotenv'), patch.dict('os.environ',{'MODEL_TIMEOUT_SECONDS':'25'}):
            self.assertEqual(load_settings().provider_timeout_seconds,25)
