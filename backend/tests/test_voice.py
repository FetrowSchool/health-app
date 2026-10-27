"""Fictional HTTP-only bootstrap tests. Every upstream request is MockTransport."""
import asyncio
from contextlib import closing
from dataclasses import replace
import json
import hashlib
import os
from pathlib import Path
import sqlite3
import tempfile
import time
import unittest
from unittest.mock import patch, AsyncMock

import httpx
from fastapi.testclient import TestClient
from backend.app.config import Settings, load_settings
from backend.app.main import create_app
from backend.app.voice_models import MAX_REQUEST_BYTES, MAX_RESPONSE_BYTES, MAX_SDP_BYTES
from backend.app.voice_provider import VOICE_ENDPOINT

PRIVATE = 'FICTIONAL_PRIVATE_SENTINEL'
OFFER = '\r\n'.join([
    'v=0', 'o=- 12345 2 IN IP4 127.0.0.1', 's=-', 't=0 0',
    'a=group:BUNDLE 0 1', 'm=audio 9 UDP/TLS/RTP/SAVPF 111',
    'c=IN IP4 0.0.0.0', 'a=mid:0', 'a=ice-ufrag:fictional',
    'a=ice-pwd:fictional-transport-password',
    'a=fingerprint:sha-256 ' + ':'.join(['AB'] * 32),
    'a=setup:actpass', 'a=sendrecv', 'a=rtcp-mux', 'a=rtpmap:111 opus/48000/2',
    'm=application 9 UDP/DTLS/SCTP webrtc-datachannel', 'a=mid:1', 'a=sctp-port:5000', '',
])
ANSWER = OFFER.replace('a=setup:actpass', 'a=setup:active')


def valid_response():
    return {'session': {'id': 'opaque_live-test_123', 'private': PRIVATE},
            'transport': {'type': 'webrtc', 'sdp': ANSWER}, 'private': PRIVATE}


class VoiceTests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory(); self.addCleanup(folder.cleanup)
        self.settings = Settings(database_path=Path(folder.name) / 'app.sqlite3', voice_api_key=PRIVATE,
                                 voice_backend_model='fictional-responses-model')
        self.calls = []
        self.behavior = lambda request: httpx.Response(201, json=valid_response())
        async def handler(request):
            self.calls.append(request)
            result = self.behavior(request)
            return await result if hasattr(result, '__await__') else result
        self.transport = httpx.MockTransport(handler)
        self.client = self.enterContext(TestClient(create_app(self.settings, voice_transport=self.transport)))

    def post(self, **overrides):
        return self.client.post('/api/voice/sessions', json={'sdp': OFFER, **overrides})

    def assert_safe_error(self, response, status):
        self.assertEqual(response.status_code, status, response.text)
        self.assertEqual(set(response.json()), {'detail'})
        self.assertNotIn(PRIVATE, response.text)
        self.assertNotIn('v=0', response.text)
        self.assertNotIn('Authorization', response.text)
        self.assertEqual(response.headers['cache-control'], 'no-store')

    def test_config_reports_only_status_and_duration_without_provider_call(self):
        r = self.client.get('/api/voice/config')
        self.assertEqual(r.json(), {'status': 'configured', 'duration_seconds': 60})
        self.assertEqual(r.headers['cache-control'], 'no-store')
        self.assertEqual(self.calls, [])
        self.assertNotIn(PRIVATE, repr(self.settings))

    def test_missing_key_does_not_reuse_text_provider_key_or_make_call(self):
        settings = replace(self.settings, voice_api_key='', model_api_key=PRIVATE, model_provider='live')
        with TestClient(create_app(settings, voice_transport=self.transport)) as client:
            self.assertEqual(client.get('/api/voice/config').json(), {'status': 'unconfigured', 'duration_seconds': 60})
            self.assert_safe_error(client.post('/api/voice/sessions', json={'sdp': OFFER}), 503)
        self.assertEqual(self.calls, [])

    def test_invalid_key_is_unconfigured_not_echoed(self):
        with TestClient(create_app(replace(self.settings, voice_api_key=PRIVATE+'\nHeader: secret'), voice_transport=self.transport)) as client:
            self.assertEqual(client.get('/api/voice/config').json()['status'], 'unconfigured')
            self.assert_safe_error(client.post('/api/voice/sessions', json={'sdp': OFFER}), 503)
        self.assertEqual(self.calls, [])

    def test_legacy_backend_model_does_not_override_exact_session_config(self):
        for model in ['', 'fictional-override']:
            with TestClient(create_app(replace(self.settings, voice_backend_model=model), voice_transport=self.transport)) as client:
                self.assertEqual(client.get('/api/voice/config').json()['status'], 'configured')
                self.assertEqual(client.post('/api/voice/sessions', json={'sdp': OFFER}).status_code, 201)
        for request in self.calls:
            self.assertEqual(json.loads(request.content)['session']['delegation']['responses']['model'], 'gpt-6-luna')

    def test_success_sends_full_config_with_separate_prompt_layers_and_projects_response(self):
        r = self.post()
        self.assertEqual(r.status_code, 201, r.text)
        self.assertEqual(r.json(), {'session_id': 'opaque_live-test_123', 'sdp': ANSWER, 'duration_seconds': 60})
        self.assertNotIn(PRIVATE, r.text)
        self.assertEqual(len(self.calls), 1)
        request = self.calls[0]
        self.assertEqual(str(request.url), VOICE_ENDPOINT)
        self.assertEqual(request.headers['authorization'], 'Bearer '+PRIVATE)
        expected = {"model": "gpt-live-1", "audio": {"output": {"voice": "gleam"}},
                    "delegation": {"type": "responses", "responses": {"parallel_tool_calls": False,
                    "model": "gpt-6-luna", "reasoning": {"effort": "medium"}, "tools": [{"type": "web_search"}]}}}
        active = json.loads(Path('backend/app/voice_session.json').read_text())
        expected['instructions'] = active['instructions']
        expected['delegation']['responses']['instructions'] = active['delegation']['responses']['instructions']
        self.assertNotEqual(expected['instructions'], expected['delegation']['responses']['instructions'])
        self.assertIn('not a therapist', expected['instructions'])
        self.assertEqual(json.loads(request.content), {'session': expected, 'transport': {'type': 'webrtc', 'sdp': OFFER}})
        self.assertLessEqual(request.extensions['timeout']['read'], 10)
        self.assertEqual(r.headers['cache-control'], 'no-store')

    def test_distinctive_prompt_reaches_outgoing_request_and_reload_requires_new_provider(self):
        marker = "When the user asks for help organizing schoolwork, provide one concrete organizational suggestion before asking a question."
        backend = "Provide separate, nonclinical reasoning using supplied context only."
        config = json.loads(Path('backend/app/voice_session.json').read_text())
        config['instructions'] = marker
        config['delegation']['responses']['instructions'] = backend
        with tempfile.TemporaryDirectory() as folder:
            file = Path(folder) / 'voice_session.json'; file.write_text(json.dumps(config))
            with patch('backend.app.voice_provider.SESSION_CONFIG_PATH', file):
                app = create_app(self.settings, voice_transport=self.transport)
                with TestClient(app) as client:
                    first = client.post('/api/voice/sessions', json={'sdp': OFFER})
                    self.assertEqual(first.status_code, 201)
                    sent = json.loads(self.calls[-1].content)['session']
                    self.assertEqual(sent['instructions'], marker)
                    self.assertEqual(sent['delegation']['responses']['instructions'], backend)
                    config['instructions'] = 'Updated harmless conversation instruction.'
                    file.write_text(json.dumps(config))
                    self.assertEqual(client.post('/api/voice/sessions', json={'sdp': OFFER}).status_code, 201)
                    self.assertEqual(json.loads(self.calls[-1].content)['session']['instructions'], marker)
                    self.assertEqual(set(first.json()), {'session_id','sdp','duration_seconds'})
                    self.assertNotIn(marker, client.get('/api/voice/config').text+first.text)
                with TestClient(create_app(self.settings, voice_transport=self.transport)) as fresh:
                    self.assertEqual(fresh.post('/api/voice/sessions', json={'sdp': OFFER}).status_code, 201)
                    self.assertEqual(json.loads(self.calls[-1].content)['session']['instructions'], config['instructions'])
        self.assertEqual(len(self.calls), 3)
        self.assertTrue(all(str(r.url) == VOICE_ENDPOINT and r.method == 'POST' for r in self.calls))

    def test_prompt_fingerprints_are_opt_in_match_actual_payload_and_never_log_text(self):
        marker = 'Distinctive harmless prompt for a fictional schoolwork test.'
        backend = 'Separate backend policy for a fictional test.'
        config = json.loads(Path('backend/app/voice_session.json').read_text())
        config['instructions'] = marker
        config['delegation']['responses']['instructions'] = backend
        with tempfile.TemporaryDirectory() as folder:
            file = Path(folder) / 'voice_session.json'; file.write_text(json.dumps(config))
            with patch('backend.app.voice_provider.SESSION_CONFIG_PATH', file):
                with self.assertNoLogs('pause.voice.prompts'):
                    with TestClient(create_app(self.settings, voice_transport=self.transport)) as client:
                        self.assertEqual(client.post('/api/voice/sessions', json={'sdp': OFFER}).status_code, 201)
                settings = replace(self.settings, voice_diagnostics=True)
                with self.assertLogs('pause.voice.prompts', level='WARNING') as logs:
                    with TestClient(create_app(settings, voice_transport=self.transport)) as client:
                        self.assertEqual(client.post('/api/voice/sessions', json={'sdp': OFFER}).status_code, 201)
                self.assertEqual(len(logs.output), 2)
                self.assertIn('phase=loaded source=voice_session.json', logs.output[0])
                self.assertIn('phase=outgoing source=voice_session.json', logs.output[1])
                actual = json.loads(self.calls[-1].content)['session']['instructions']
                for line in logs.output:
                    self.assertIn('live_hash='+hashlib.sha256(actual.encode()).hexdigest(), line)
                    self.assertIn('live_chars='+str(len(actual)), line)
                    self.assertIn('included=True', line)
                    self.assertIn('backend_hash='+hashlib.sha256(backend.encode()).hexdigest(), line)
                    for private in [marker, backend, PRIVATE, OFFER]: self.assertNotIn(private, line)

    def test_development_diagnostics_are_opt_in_and_never_log_provider_text(self):
        self.behavior = lambda request: httpx.Response(401, json={'error': {'code': 'invalid_api_key', 'message': PRIVATE}})
        with self.assertNoLogs('pause.voice.diagnostics'):
            self.assert_safe_error(self.post(), 502)
        self.client.app.state.voice_provider.settings = replace(self.settings, voice_diagnostics=True)
        cases = [(401, 'invalid_api_key', 'authentication'), (403, 'permission_denied', 'access_denied'),
                 (429, 'insufficient_quota', 'credits_or_quota'), (404, 'model_not_found', 'model_access'),
                 (400, 'unsupported_parameter', 'unsupported_setting'), (400, PRIVATE, 'invalid_request')]
        for status, code, category in cases:
            self.behavior = lambda request: httpx.Response(status, json={'error': {'code': code, 'message': PRIVATE,
                                                                                 'param': PRIVATE}})
            with self.assertLogs('pause.voice.diagnostics', level='WARNING') as logs:
                self.assert_safe_error(self.post(), 502)
            self.assertEqual(len(logs.output), 1)
            self.assertIn('stage=provider_response', logs.output[0])
            self.assertIn('upstream_status='+str(status), logs.output[0])
            self.assertIn('category='+category, logs.output[0])
            for secret in [PRIVATE, OFFER, ANSWER, 'Authorization', 'Bearer']:
                self.assertNotIn(secret, logs.output[0])

    def test_diagnostics_distinguish_transport_timeout_and_invalid_answer(self):
        self.client.app.state.voice_provider.settings = replace(self.settings, voice_diagnostics=True)
        for error, category, status in [(httpx.ConnectError(PRIVATE), 'transport_error', 502),
                                         (httpx.ReadTimeout(PRIVATE), 'timeout', 504)]:
            def fail(request): raise error
            self.behavior = fail
            with self.assertLogs('pause.voice.diagnostics', level='WARNING') as logs:
                self.assert_safe_error(self.post(), status)
            self.assertIn('stage=provider_request', logs.output[0])
            self.assertIn('category='+category, logs.output[0])
            self.assertNotIn(PRIVATE, logs.output[0])
        self.behavior = lambda request: httpx.Response(201, json={'session': {'id': 'fictional'},
                                                                'transport': {'type': 'webrtc', 'sdp': PRIVATE}})
        with self.assertLogs('pause.voice.diagnostics', level='WARNING') as logs:
            self.assert_safe_error(self.post(), 502)
        self.assertIn('stage=answer_validation upstream_status=201 category=malformed_answer', logs.output[0])
        self.assertNotIn(PRIVATE, logs.output[0])

    def test_browser_configuration_and_invented_owner_are_rejected(self):
        for field in ['session','transport','model','models','backend_model','VOICE_BACKEND_MODEL','responses','api_key','instructions','prompt','policy','provider_url','tools','store','duration_seconds','profile_id','owner_id','allowed_client_events','delegation']:
            self.assert_safe_error(self.post(**{field: PRIVATE}), 422)
        self.assert_safe_error(self.client.post('/api/voice/sessions?model='+PRIVATE, json={'sdp': OFFER}), 422)
        self.assert_safe_error(self.client.get('/api/voice/config?model='+PRIVATE), 422)
        self.assertEqual(self.calls, [])

    def test_no_profile_or_owner_required_and_no_database_writes(self):
        with closing(sqlite3.connect(self.settings.database_path)) as c:
            before = {t:c.execute('select * from '+t).fetchall() for t in ['exercise_sessions','conversations','messages','daily_mood_checkins']}
        self.assertEqual(self.post().status_code, 201)
        with closing(sqlite3.connect(self.settings.database_path)) as c:
            for table, rows in before.items(): self.assertEqual(c.execute('select * from '+table).fetchall(), rows)

    def test_invalid_sdp_and_invalid_body_types_are_sanitized(self):
        for value in ['', '  ', PRIVATE, 'v=0\n', None, 123, True, {}, [], ANSWER, OFFER.replace('v=0','v=1'), OFFER+'\0', OFFER.replace('AB:AB','AB'), OFFER.replace('webrtc-datachannel','unrelated')]:
            self.assert_safe_error(self.post(sdp=value), 422)
        for body in [{}, [], None, {'sdp': OFFER, 'private': PRIVATE}]:
            self.assert_safe_error(self.client.post('/api/voice/sessions', content=json.dumps(body), headers={'Content-Type':'application/json'}), 422)
        self.assertEqual(self.calls, [])

    def test_byte_limits_reject_ascii_and_unicode_sdp(self):
        for sdp in [OFFER+'a=x:'+'x'*MAX_SDP_BYTES, OFFER+'a=x:'+'é'*(MAX_SDP_BYTES//2)]:
            self.assert_safe_error(self.post(sdp=sdp), 413)
        self.assertEqual(self.calls, [])

    def test_request_bound_enforced_for_chunked_or_false_length(self):
        body = b'x'*(MAX_REQUEST_BYTES+1)
        self.assert_safe_error(self.client.post('/api/voice/sessions', content=iter([body[:50000],body[50000:]]), headers={'Content-Type':'application/json'}),413)
        self.assert_safe_error(self.client.post('/api/voice/sessions', content=body, headers={'Content-Type':'application/json','Content-Length':'1'}),413)
        self.assertEqual(self.calls, [])

    def test_json_syntax_duplicates_and_media_type_are_sanitized(self):
        for body in [b'{', b'\xff', b'{"sdp": NaN}', b'{"sdp":"'+PRIVATE.encode()+b'","sdp":"duplicate"}']:
            self.assert_safe_error(self.client.post('/api/voice/sessions', content=body, headers={'Content-Type':'application/json'}),400)
        self.assert_safe_error(self.client.post('/api/voice/sessions', content=OFFER, headers={'Content-Type':'text/plain'}),415)
        self.assertEqual(self.calls, [])

    def test_http_provider_errors_do_not_leak_or_retry(self):
        for status in [400,401,403,429,500,503,302,200]:
            self.behavior = lambda request: httpx.Response(status, text=PRIVATE, headers={'Location':'https://untrusted.invalid/'+PRIVATE})
            before = len(self.calls)
            self.assert_safe_error(self.post(), 502)
            self.assertEqual(len(self.calls), before+1)

    def test_transport_error_and_timeout_are_sanitized_without_retry(self):
        for error, status in [(httpx.ConnectError(PRIVATE),502),(httpx.ReadTimeout(PRIVATE),504),(RuntimeError(PRIVATE),502)]:
            def fail(request): raise error
            self.behavior = fail
            before = len(self.calls)
            self.assert_safe_error(self.post(), status)
            self.assertEqual(len(self.calls), before+1)

    def test_total_deadline_bounds_even_a_slow_transport(self):
        async def slow(request):
            await asyncio.sleep(1)
            return httpx.Response(201,json=valid_response())
        self.behavior = slow
        with TestClient(create_app(replace(self.settings,voice_timeout_seconds=0.1),voice_transport=self.transport)) as client:
            start = time.monotonic()
            self.assert_safe_error(client.post('/api/voice/sessions',json={'sdp':OFFER}),504)
            self.assertLess(time.monotonic()-start,0.8)
        self.assertEqual(len(self.calls),1)

    def test_malformed_provider_shapes_and_opaque_ids_rejected(self):
        variants = [None, [], {}, {'session':None,'transport':{}},
                    {'session':{'id':123},'transport':{'type':'webrtc','sdp':ANSWER}},
                    {'session':{'id':''},'transport':{'type':'webrtc','sdp':ANSWER}},
                    {'session':{'id':'bad\nid'},'transport':{'type':'webrtc','sdp':ANSWER}},
                    {'session':{'id':'x'*257},'transport':{'type':'webrtc','sdp':ANSWER}},
                    {'session':{'id':'opaque_123'},'transport':{'type':'sip','sdp':ANSWER}},
                    {'session':{'id':'opaque_123'},'transport':{'type':'webrtc','sdp':123}},
                    {'session':{'id':'opaque_123'},'transport':{'type':'webrtc','sdp':OFFER}},
                    {'session':{'id':'opaque_123'},'transport':{'type':'webrtc','sdp':PRIVATE}}]
        for data in variants:
            self.behavior = lambda request: httpx.Response(201,json=data)
            self.assert_safe_error(self.post(),502)

    def test_malformed_non_json_duplicate_and_oversized_provider_responses(self):
        for content, content_type in [(b'{','application/json'), (PRIVATE.encode(),'text/html'),
                                      (b'{"session":{},"session":{}}','application/json'),
                                      (b'x'*(MAX_RESPONSE_BYTES+1),'application/json')]:
            self.behavior = lambda request: httpx.Response(201,content=content,headers={'Content-Type':content_type})
            self.assert_safe_error(self.post(),502)

    def test_duration_is_server_owned_and_configuration_is_bounded(self):
        with TestClient(create_app(replace(self.settings,voice_duration_seconds=90),voice_transport=self.transport)) as client:
            self.assertEqual(client.get('/api/voice/config').json()['duration_seconds'],90)
            self.assertEqual(client.post('/api/voice/sessions',json={'sdp':OFFER}).json()['duration_seconds'],90)
        for updates in [{'voice_duration_seconds':0},{'voice_duration_seconds':301},{'voice_duration_seconds':True}, {'voice_timeout_seconds':float('nan')},{'voice_timeout_seconds':float('inf')},{'voice_timeout_seconds':0},{'voice_timeout_seconds':26}]:
            with self.assertRaises(ValueError): replace(self.settings,**updates)

    def test_env_names_load_without_changing_existing_file_or_text_settings(self):
        with patch('backend.app.config.load_dotenv') as dotenv, patch.dict(os.environ,{
            'OPENAI_API_KEY':PRIVATE, 'VOICE_SESSION_DURATION_SECONDS':'75', 'VOICE_PROVIDER_TIMEOUT_SECONDS':'8',
            'VOICE_BACKEND_MODEL':'  fictional-responses-model  ',
            'MODEL_PROVIDER':'mock','MODEL_API_KEY':'fictional-text-key',
        }):
            settings=load_settings()
            self.assertTrue(settings.voice_configured); self.assertEqual(settings.voice_duration_seconds,75)
            self.assertEqual(settings.voice_backend_model,'fictional-responses-model')
            self.assertEqual(settings.voice_timeout_seconds,8); self.assertEqual(settings.model_provider,'mock')
            dotenv.assert_called_once(); self.assertFalse(dotenv.call_args.kwargs['override'])
            self.assertNotIn(PRIVATE,repr(settings))
        with patch('backend.app.config.load_dotenv'), patch.dict(os.environ,{'VOICE_SESSION_DURATION_SECONDS':PRIVATE}):
            with self.assertRaisesRegex(ValueError,'Invalid voice duration or timeout configuration') as caught: load_settings()
            self.assertNotIn(PRIVATE,str(caught.exception))

    def test_existing_health_contract_remains_unchanged(self):
        r = self.client.get('/api/health')
        self.assertEqual(r.json(),{'status':'ok','database':'ready','model_configured':False})
        self.assertEqual(self.calls,[])

    def close(self, session_id='opaque_live-test_123'):
        return self.client.post('/api/voice/sessions/close', json={'session_id': session_id})

    def test_hangup_only_issued_id_is_server_owned_bounded_and_idempotent(self):
        self.assertEqual(self.post().status_code, 201)
        self.behavior = lambda request: httpx.Response(204)
        for _ in range(2):
            response = self.close()
            self.assertEqual(response.json(), {'status': 'close_requested'})
            self.assertEqual(response.headers['cache-control'], 'no-store')
        self.assertEqual(len(self.calls), 2) # One creation + one hangup, no repeated provider call.
        request = self.calls[-1]
        self.assertEqual(str(request.url), VOICE_ENDPOINT+'/opaque_live-test_123/hangup')
        self.assertEqual(request.method, 'POST'); self.assertEqual(request.content, b'')
        self.assertEqual(request.headers['authorization'], 'Bearer '+PRIVATE)
        self.assertLessEqual(request.extensions['timeout']['read'], 3)
        self.assertNotIn(PRIVATE, response.text)

    def test_unknown_expired_and_invalid_close_ids_never_call_provider(self):
        self.assert_safe_error(self.close('not-created-here'), 404)
        for body in [{}, {'session_id': ''}, {'session_id': 'bad\nid'}, {'session_id': 'x'*257},
                     {'session_id': 123}, {'session_id': 'id', 'provider_url': PRIVATE},
                     {'session_id': 'id', 'api_key': PRIVATE}, {'session_id': 'id', 'owner_id': PRIVATE}]:
            self.assert_safe_error(self.client.post('/api/voice/sessions/close', json=body), 422)
        self.assert_safe_error(self.client.post('/api/voice/sessions/close?model='+PRIVATE, json={'session_id': 'id'}), 422)
        self.assert_safe_error(self.client.post('/api/voice/sessions/close', content='x'*1025, headers={'Content-Type': 'application/json'}), 413)
        self.assertEqual(self.calls, [])
        self.assertEqual(self.post().status_code, 201)
        self.client.app.state.voice_provider.issued['opaque_live-test_123']['expires'] = 0
        self.assert_safe_error(self.close(), 404)
        self.assertEqual(len(self.calls), 1)

    def test_concurrent_hangups_share_one_upstream_request(self):
        self.assertEqual(self.post().status_code, 201)
        async def slow(request):
            await asyncio.sleep(0.01)
            return httpx.Response(200)
        self.behavior = slow
        async def run():
            provider = self.client.app.state.voice_provider
            await asyncio.gather(provider.close('opaque_live-test_123'), provider.close('opaque_live-test_123'))
        asyncio.run(run())
        self.assertEqual(len(self.calls), 2)

    def test_hangup_errors_are_sanitized_and_never_retried_even_on_repeated_end(self):
        self.assertEqual(self.post().status_code, 201)
        self.behavior = lambda request: httpx.Response(500, text=PRIVATE)
        self.assert_safe_error(self.close(), 502)
        self.assert_safe_error(self.close(), 502)
        self.assertEqual(len(self.calls), 2)

    def test_hangup_timeout_still_returns_finite_sanitized_failure(self):
        settings = replace(self.settings, voice_timeout_seconds=0.1)
        with TestClient(create_app(settings, voice_transport=self.transport)) as client:
            self.assertEqual(client.post('/api/voice/sessions', json={'sdp': OFFER}).status_code, 201)
            async def slow(request):
                await asyncio.sleep(1)
                return httpx.Response(204)
            self.behavior = slow
            start = time.monotonic()
            self.assert_safe_error(client.post('/api/voice/sessions/close', json={'session_id': 'opaque_live-test_123'}), 504)
            self.assertLess(time.monotonic()-start, 0.8)
        self.assertEqual(len(self.calls), 2)

    def test_opaque_issued_id_is_url_encoded_not_interpolated_as_a_path(self):
        data = valid_response(); data['session']['id'] = 'opaque/id?fictional'
        self.behavior = lambda request: httpx.Response(201, json=data)
        self.assertEqual(self.post().status_code, 201)
        self.behavior = lambda request: httpx.Response(204)
        self.assertEqual(self.close(data['session']['id']).status_code, 200)
        self.assertIn(b'opaque%2Fid%3Ffictional/hangup', self.calls[-1].url.raw_path)

    def test_disconnected_creation_response_is_hung_up_without_returning_sdp(self):
        self.behavior = lambda request: httpx.Response(204) if request.url.path.endswith('/hangup') else httpx.Response(201, json=valid_response())
        with patch('starlette.requests.Request.is_disconnected', new_callable=AsyncMock, return_value=True):
            self.assert_safe_error(self.post(), 499)
        self.assertEqual(len(self.calls), 2)
        self.assertTrue(self.calls[-1].url.path.endswith('/hangup'))

    def test_close_preserves_database_records_and_registry_capacity_is_bounded(self):
        tables = ['exercise_sessions', 'conversations', 'messages', 'daily_mood_checkins']
        with closing(sqlite3.connect(self.settings.database_path)) as c:
            before = {t: c.execute('select * from '+t).fetchall() for t in tables}
        self.assertEqual(self.post().status_code, 201)
        self.behavior = lambda request: httpx.Response(204)
        self.assertEqual(self.close().status_code, 200)
        with closing(sqlite3.connect(self.settings.database_path)) as c:
            for table in tables: self.assertEqual(c.execute('select * from '+table).fetchall(), before[table])
        provider = self.client.app.state.voice_provider
        provider.pending_creates = 256
        count = len(self.calls)
        self.assert_safe_error(self.post(), 502)
        self.assertEqual(len(self.calls), count)
