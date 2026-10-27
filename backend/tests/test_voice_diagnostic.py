"""Fictional provider responses only. The isolated app must never open SQLite."""
import json
import sqlite3
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch
import httpx
from fastapi.testclient import TestClient
from backend.app.config import Settings
from backend.app.voice_diagnostic import create_diagnostic_app, INSTRUCTIONS
from backend.tests.test_voice import OFFER, ANSWER, PRIVATE


class VoiceDiagnosticTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.database = Path(self.folder.name) / 'must-not-exist.sqlite3'
        self.settings = Settings(database_path=self.database, voice_api_key=PRIVATE,
                                 voice_live_model='gpt-live-1', voice_diagnostics=True)
        self.requests = []

    def handler(self, request):
        self.requests.append(request)
        if request.url.path.endswith('/hangup'):
            return httpx.Response(204)
        return httpx.Response(201, json={'session': {'id': 'opaque-diagnostic'},
                                        'transport': {'type': 'webrtc', 'sdp': ANSWER}})

    def test_database_free_minimal_round_trip_and_close_preserve_contract(self):
        app = create_diagnostic_app(self.settings, transport=httpx.MockTransport(self.handler))
        with patch.object(sqlite3, 'connect', side_effect=AssertionError('SQLite must not be used')):
            with TestClient(app) as client:
                self.assertIsNotNone(app.state.voice_provider.client)
                self.assertEqual(client.get('/api/voice/config').json(), {'status': 'configured', 'duration_seconds': 30})
                response = client.post('/api/voice/sessions', json={'sdp': OFFER})
                self.assertEqual(response.status_code, 201)
                self.assertEqual(response.json(), {'session_id': 'opaque-diagnostic', 'sdp': ANSWER, 'duration_seconds': 30})
                request = self.requests[0]
                self.assertEqual(str(request.url), 'https://api.openai.com/v1/live/sessions')
                self.assertEqual(request.method, 'POST')
                self.assertEqual(json.loads(request.content), {'session': {'model': 'gpt-live-1', 'instructions': INSTRUCTIONS,
                    'store': False, 'triggers': []}, 'transport': {'type': 'webrtc', 'sdp': OFFER}})
                self.assertEqual(int(request.headers['content-length']), len(request.content))
                self.assertNotIn('transfer-encoding', request.headers)
                self.assertNotIn(PRIVATE, response.text)
                self.assertEqual(client.post('/api/voice/sessions/close', json={'session_id': 'opaque-diagnostic'}).status_code, 200)
                self.assertEqual(len(self.requests), 2)
                self.assertNotIn('/api/recommendations', app.openapi()['paths'])
            self.assertIsNone(app.state.voice_provider.client)
        self.assertFalse(self.database.exists())

    def test_unconfigured_and_browser_configuration_reject_without_upstream_request(self):
        app = create_diagnostic_app(replace(self.settings, voice_api_key=''), transport=httpx.MockTransport(self.handler))
        with TestClient(app) as client:
            self.assertEqual(client.get('/api/voice/config').json()['status'], 'unconfigured')
            self.assertEqual(client.post('/api/voice/sessions', json={'sdp': OFFER}).status_code, 503)
            self.assertEqual(client.post('/api/voice/sessions', json={'sdp': OFFER, 'model': PRIVATE}).status_code, 422)
        self.assertEqual(self.requests, [])

    def test_diagnostic_model_is_exact_and_has_no_provider_substitution(self):
        with self.assertRaisesRegex(ValueError, 'must be gpt-live-1'):
            create_diagnostic_app(replace(self.settings, voice_live_model='other'))

    def test_upload_completion_read_timeout_and_secret_free_telemetry(self):
        async def handler(request):
            self.requests.append(request)
            await request.extensions['trace']('connection.start_tls.complete', {'private': PRIVATE})
            await request.extensions['trace']('http11.send_request_body.complete', {'private': PRIVATE})
            await request.extensions['trace']('http11.receive_response_headers.started', {'private': PRIVATE})
            raise httpx.ReadTimeout(PRIVATE)
        app = create_diagnostic_app(self.settings, transport=httpx.MockTransport(handler))
        with TestClient(app) as client, self.assertLogs('pause.voice.diagnostics', level='WARNING') as logs:
            response = client.post('/api/voice/sessions', json={'sdp': OFFER})
        self.assertEqual(response.status_code, 504)
        self.assertEqual(len(self.requests), 1)
        self.assertIn('phase=awaiting_headers timeout_kind=read', logs.output[0])
        self.assertNotIn(PRIVATE, '\n'.join(logs.output)+response.text)
        self.assertNotIn(OFFER, '\n'.join(logs.output))

    def test_bad_answer_and_auth_failure_remain_sanitized(self):
        for status, body, public in [(401, {'error': {'code': 'invalid_api_key', 'message': PRIVATE}}, 502),
                                    (201, {'session': {'id': 'opaque'}, 'transport': {'type': 'webrtc', 'sdp': PRIVATE}}, 502)]:
            with TestClient(create_diagnostic_app(self.settings, transport=httpx.MockTransport(lambda r: httpx.Response(status, json=body)))) as client:
                response = client.post('/api/voice/sessions', json={'sdp': OFFER})
                self.assertEqual(response.status_code, public)
                self.assertNotIn(PRIVATE, response.text)

    def test_connect_write_pool_and_os_timeouts_are_distinct_without_raw_errors(self):
        cases = [(httpx.ConnectTimeout(PRIVATE), 'connect'), (httpx.WriteTimeout(PRIVATE), 'write'),
                 (httpx.PoolTimeout(PRIVATE), 'pool'), (TimeoutError(60, PRIVATE), 'os_timeout')]
        for error, kind in cases:
            async def handler(request):
                raise error
            with TestClient(create_diagnostic_app(self.settings, transport=httpx.MockTransport(handler))) as client:
                with self.assertLogs('pause.voice.diagnostics', level='WARNING') as logs:
                    response = client.post('/api/voice/sessions', json={'sdp': OFFER})
            self.assertEqual(response.status_code, 504)
            self.assertIn('timeout_kind='+kind, logs.output[0])
            self.assertNotIn(PRIVATE, logs.output[0]+response.text)
