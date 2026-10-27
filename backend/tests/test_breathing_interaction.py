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


class BreathingInteractionTests(unittest.TestCase):
    def setUp(self):
        folder=tempfile.TemporaryDirectory();self.addCleanup(folder.cleanup)
        self.path=Path(folder.name)/'app.sqlite3';self.settings=Settings(database_path=self.path)
        self.client=self.enterContext(TestClient(create_app(self.settings)))
        self.headers={'X-App-ID':str(uuid4())};self.start=datetime(2026,10,22,12,tzinfo=timezone.utc)
    def session(self,exercise='paced_breathing'):
        id=str(uuid4())
        r=self.client.post('/api/sessions',headers=self.headers,json={'id':id,'exercise_type':exercise,'started_at':self.start.isoformat(),'entry_duration_seconds':0.001})
        self.assertEqual(r.status_code,200,r.text);return id
    def body(self,seconds=60,**metrics):
        return dict(status='completed' if seconds>=60 else 'exited',ended_at=(self.start+timedelta(seconds=seconds)).isoformat(),duration_seconds=seconds,**metrics)
    def end(self,id,body):return self.client.patch('/api/sessions/'+id,headers=self.headers,json=body)
    def test_each_mode_persists_optional_summary_and_survives_restart(self):
        for mode in ['hold','tap','observe','mixed']:
            id=self.session();n=0 if mode=='observe' else 4
            body=self.body(interaction_mode=mode,inhale_interactions=n,exhale_interactions=n,completed_cycles=6)
            r=self.end(id,body);self.assertEqual(r.status_code,200,r.text)
            self.assertEqual(r.json()['inhale_interactions'],n)
            self.assertEqual(self.end(id,body).json(),r.json())
            with TestClient(create_app(self.settings)) as restarted:
                self.assertEqual(restarted.get('/api/sessions/'+id,headers=self.headers).json(),r.json())
            with closing(sqlite3.connect(self.path)) as c:
                self.assertEqual(c.execute('select interaction_mode,inhale_interactions,exhale_interactions,completed_cycles from exercise_sessions where id=?',(id,)).fetchone(),(mode,n,n,6))
    def test_legacy_clients_and_grounding_keep_null_metrics(self):
        for exercise in ['paced_breathing','grounding_54321','stop']:
            r=self.end(self.session(exercise),self.body());self.assertEqual(r.status_code,200)
            self.assertIsNone(r.json()['interaction_mode']);self.assertIsNone(r.json()['completed_cycles'])
    def test_invalid_partial_fabricated_or_wrong_skill_metrics_reject(self):
        valid=dict(interaction_mode='hold',inhale_interactions=1,exhale_interactions=0,completed_cycles=0)
        for metrics in [dict(interaction_mode='hold'),{**valid,'inhale_interactions':7},{**valid,'inhale_interactions':True},{**valid,'completed_cycles':1},{**valid,'exhale_interactions':1},{**valid,'interaction_mode':'observe'},{**valid,'interaction_mode':'unknown'}]:
            self.assertEqual(self.end(self.session(),self.body(2,**metrics)).status_code,422)
        self.assertEqual(self.end(self.session('grounding_54321'),self.body(2,**valid)).status_code,422)
    def test_exit_summary_immutable_and_scoped(self):
        id=self.session();body=self.body(14,interaction_mode='mixed',inhale_interactions=2,exhale_interactions=1,completed_cycles=1)
        self.assertEqual(self.end(id,body).status_code,200)
        self.assertEqual(self.end(id,{**body,'inhale_interactions':1}).status_code,409)
        self.assertEqual(self.client.get('/api/sessions/'+id,headers={'X-App-ID':str(uuid4())}).status_code,404)
    def test_v5_migration_preserves_every_old_column_and_is_idempotent(self):
        id=self.session()
        with closing(sqlite3.connect(self.path)) as c,c:
            for field in ['interaction_mode','inhale_interactions','exhale_interactions','completed_cycles']:
                c.execute('alter table exercise_sessions drop column '+field)
            c.execute("update app_metadata set value='5' where key='schema_version'")
            cols=[r[1] for r in c.execute('pragma table_info(exercise_sessions)')]
            old=c.execute('select * from exercise_sessions').fetchall()
        initialize_database(self.path);initialize_database(self.path)
        with closing(sqlite3.connect(self.path)) as c:
            self.assertEqual(c.execute('select '+','.join(cols)+' from exercise_sessions').fetchall(),old)
            self.assertEqual(c.execute('select interaction_mode,inhale_interactions,exhale_interactions,completed_cycles from exercise_sessions where id=?',(id,)).fetchone(),(None,None,None,None))
            self.assertEqual(c.execute('pragma foreign_key_check').fetchall(),[])
