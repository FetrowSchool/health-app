"""Fictional invalid model outputs; no network, credentials or real app database."""
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
from backend.app.feedback_policy import FALLBACK, predefined_message


class InvalidProvider:
    mode = 'mock'

    def __init__(self):
        self.output = ''
        self.contexts = []

    async def generate(self, context):
        self.contexts.append(context)
        return self.output


class BehaviorBoundaryTests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.path = Path(folder.name) / 'fictional.sqlite3'
        self.provider = InvalidProvider()
        self.client = self.enterContext(TestClient(create_app(Settings(database_path=self.path), self.provider)))
        self.headers = {'X-App-ID': str(uuid4())}
        self.start = datetime(2026, 11, 2, 12, tzinfo=timezone.utc)

    def completed(self, headers=None):
        headers = headers or self.headers
        id = str(uuid4())
        self.assertEqual(self.client.post('/api/sessions', headers=headers, json={
            'id': id, 'exercise_type': 'grounding_54321', 'started_at': self.start.isoformat(),
            'entry_duration_seconds': 0,
        }).status_code, 200)
        self.assertEqual(self.client.patch('/api/sessions/' + id, headers=headers, json={
            'status': 'completed', 'ended_at': (self.start + timedelta(seconds=70)).isoformat(),
            'duration_seconds': 70,
        }).status_code, 200)
        return id

    def feedback(self, session, headers=None):
        return self.client.post('/api/feedback-response', headers=headers or self.headers, json={
            'request_id': str(uuid4()), 'session_id': session, 'exercise_type': 'grounding_54321',
            'feedback': 'helpful', 'local_date': '2026-11-02',
            'user_message': predefined_message('grounding_54321', 'helpful'),
        })

    def test_bc3_seven_invalid_feedback_outputs_rejected_without_exercise_mutation(self):
        cases = {
            'timing': {'inhale_seconds': 1, 'exhale_seconds': 1},
            'instructions': 'Replace Grounding with a different first step.',
            'autostart': {'navigate': 'paced_breathing', 'start': True},
            'hide_support': '<script>removeCrisisSupport()</script>',
            'history_tool': {'tool_calls': [{'name': 'history.read', 'owner': 'another-fictional-owner'}]},
            'unsupported_exercise': 'Try Unsupported Exercise XYZ.',
            'professional_therapy': 'I provide professional therapy.',
        }
        for label, output in cases.items():
            with self.subTest(boundary=label):
                session = self.completed()
                before = self.client.get('/api/sessions/' + session, headers=self.headers).json()
                self.provider.output = output
                result = self.feedback(session)
                self.assertEqual(result.status_code, 200)
                record = result.json()
                self.assertEqual((record['status'], record['failure_code']), ('failed', 'invalid_response'))
                self.assertEqual(record['fallback_message'], FALLBACK)
                self.assertEqual([m['role'] for m in record['messages']], ['user'])
                self.assertEqual(self.client.get('/api/sessions/' + session, headers=self.headers).json(), before)
        with closing(sqlite3.connect(self.path)) as connection:
            self.assertEqual(connection.execute("SELECT count(*) FROM messages WHERE role='assistant'").fetchone()[0], 0)
            self.assertEqual(connection.execute('PRAGMA foreign_key_check').fetchall(), [])
        self.assertEqual(len(self.provider.contexts), 7)

    def test_bc3_other_identity_history_and_messages_excluded_from_generation(self):
        other = {'X-App-ID': str(uuid4())}
        private_session = self.completed(other)
        self.provider.output = 'Feedback noted. You can choose what to do next.'
        private_conversation = self.feedback(private_session, other).json()
        self.assertEqual(private_conversation['status'], 'succeeded')
        own_session = self.completed()
        self.provider.output = {'tool_calls': [{'name': 'history.read', 'conversation_id': private_conversation['id']}]}
        result = self.feedback(own_session).json()
        self.assertEqual(result['failure_code'], 'invalid_response')
        self.assertEqual(self.client.get('/api/conversations/' + private_conversation['id'], headers=self.headers).status_code, 404)
        own_history = self.client.get('/api/history', headers=self.headers).json()
        self.assertNotIn(private_conversation['id'], str(own_history))
        self.assertNotIn(private_session, str(own_history))
        context = self.provider.contexts[-1]
        self.assertEqual(set(vars(context)), {'exercise_type', 'feedback', 'user_message', 'mood', 'recent'})
        self.assertEqual(len(context.recent), 1)
        self.assertEqual(set(context.recent[0]), {'exercise_type', 'status', 'feedback'})
        for forbidden in [other['X-App-ID'], private_session, private_conversation['id']]:
            self.assertNotIn(forbidden, repr(context))

    def test_bc3_unsupported_exercise_submission_rejected_before_generation(self):
        result = self.client.post('/api/sessions', headers=self.headers, json={
            'id': str(uuid4()), 'exercise_type': 'unsupported_xyz',
            'started_at': self.start.isoformat(), 'entry_duration_seconds': 0,
        })
        self.assertEqual(result.status_code, 422)
        self.assertEqual(self.provider.contexts, [])
        with closing(sqlite3.connect(self.path)) as connection:
            self.assertEqual(connection.execute('SELECT count(*) FROM exercise_sessions').fetchone()[0], 0)
