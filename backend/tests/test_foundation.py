from contextlib import closing
from pathlib import Path
import sqlite3
import tempfile
import unittest

from fastapi.testclient import TestClient
from backend.app.config import PROJECT_ROOT, Settings
from backend.app.database import initialize_database
from backend.app.main import create_app


class FoundationTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "nested" / "app.sqlite3"
        self.settings = Settings(database_path=self.path)

    def test_health_initialization_and_no_personal_records(self):
        with TestClient(create_app(self.settings)) as client:
            response = client.get("/api/health")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {
                "status": "ok", "database": "ready", "model_configured": False,
            })
        with closing(sqlite3.connect(self.path)) as connection, connection:
            self.assertEqual(connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall(), [("app_metadata",), ("exercise_sessions",), ("daily_mood_checkins",), ("conversations",), ("messages",)])
            self.assertEqual(connection.execute("SELECT count(*) FROM exercise_sessions").fetchone(), (0,))
            self.assertEqual(connection.execute("SELECT count(*) FROM daily_mood_checkins").fetchone(), (0,))
            self.assertEqual(connection.execute("SELECT * FROM app_metadata").fetchall(), [("schema_version", "7")])

    def test_restart_preserves_metadata_without_duplicates(self):
        initialize_database(self.path)
        with closing(sqlite3.connect(self.path)) as connection, connection:
            connection.execute("INSERT INTO app_metadata VALUES (?, ?)", ("fictional_test", "preserve"))
        for _ in range(2):
            with TestClient(create_app(self.settings)) as client:
                self.assertEqual(client.get("/api/health").status_code, 200)
        with closing(sqlite3.connect(self.path)) as connection, connection:
            self.assertEqual(connection.execute("SELECT count(*) FROM app_metadata").fetchone(), (2,))
            self.assertEqual(connection.execute("SELECT value FROM app_metadata WHERE key='fictional_test'").fetchone(), ("preserve",))

    def test_unavailable_database_is_honest_and_not_recreated(self):
        with TestClient(create_app(self.settings)) as client:
            self.path.unlink()
            response = client.get("/api/health")
            self.assertEqual(response.status_code, 503)
            self.assertEqual(response.json(), {"detail": "Local database is unavailable."})
            self.assertFalse(self.path.exists())

    def test_configuration_presence_does_not_expose_key(self):
        settings = Settings(database_path=self.path, model_api_key="fictional-not-a-real-key")
        with TestClient(create_app(settings)) as client:
            response = client.get("/api/health")
            self.assertTrue(response.json()["model_configured"])
            self.assertNotIn("fictional-not-a-real-key", response.text)
            self.assertNotIn("fictional-not-a-real-key", repr(settings))

    def test_cors_allows_only_expected_origin(self):
        with TestClient(create_app(self.settings)) as client:
            for origin, allowed in [("http://127.0.0.1:5173", True), ("https://unrelated.example", False)]:
                response = client.get("/api/health", headers={"Origin": origin})
                self.assertEqual(response.headers.get("access-control-allow-origin"), origin if allowed else None)

    def test_database_path_is_project_relative(self):
        self.assertEqual(Settings().database_path, PROJECT_ROOT / "data" / "app.sqlite3")
        self.assertTrue(Settings().database_path.is_absolute())


if __name__ == "__main__":
    unittest.main()
