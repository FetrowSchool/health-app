"""Idempotent local SQLite schema; backend-only access."""
from contextlib import closing
from pathlib import Path
import sqlite3


def initialize_database(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(path, timeout=3)) as connection, connection:
        # Rebuilding SQLite CHECK constraints requires the documented table-rebuild
        # migration with foreign keys disabled before the transaction. Runtime
        # writes always enable FKs; integrity is checked before this commit.
        connection.execute("PRAGMA foreign_keys = OFF")
        connection.execute("BEGIN IMMEDIATE")
        connection.execute("""CREATE TABLE IF NOT EXISTS app_metadata (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )""")
        version = connection.execute("SELECT value FROM app_metadata WHERE key='schema_version'").fetchone()
        if version is not None and version[0] not in ('1', '2', '3', '4', '5', '6', '7'):
            raise RuntimeError("Unsupported local database schema version.")
        connection.execute("""CREATE TABLE IF NOT EXISTS exercise_sessions (
            id TEXT PRIMARY KEY,
            app_id TEXT NOT NULL,
            exercise_type TEXT NOT NULL CHECK (exercise_type IN ('paced_breathing', 'stop', 'grounding_54321')),
            started_at TEXT NOT NULL,
            ended_at TEXT,
            status TEXT NOT NULL DEFAULT 'started' CHECK (status IN ('started', 'completed', 'exited')),
            duration_seconds REAL NOT NULL DEFAULT 0 CHECK (duration_seconds >= 0),
            entry_duration_seconds REAL NOT NULL CHECK (entry_duration_seconds >= 0),
            planned_duration_seconds INTEGER NOT NULL DEFAULT 60 CHECK (planned_duration_seconds = CASE WHEN exercise_type = 'grounding_54321' THEN 70 ELSE 60 END),
            feedback TEXT CHECK (feedback IN ('helpful', 'not_helpful', 'skipped')),
            CHECK ((status = 'started' AND ended_at IS NULL AND duration_seconds = 0)
                OR (status != 'started' AND ended_at IS NOT NULL)),
            CHECK (feedback IS NULL OR status = 'completed')
        )""")
        connection.execute("""CREATE TABLE IF NOT EXISTS daily_mood_checkins (
            app_id TEXT NOT NULL,
            local_date TEXT NOT NULL,
            mood TEXT NOT NULL CHECK (mood IN ('calm','okay','anxious','overwhelmed','skipped')),
            created_at TEXT NOT NULL,
            PRIMARY KEY (app_id, local_date)
        )""")
        conversation_sql = """CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            app_id TEXT NOT NULL,
            session_id TEXT REFERENCES exercise_sessions(id) ON DELETE CASCADE,
            exercise_type TEXT CHECK (exercise_type IN ('paced_breathing','stop','grounding_54321')),
            feedback TEXT CHECK (feedback IN ('helpful','not_helpful')),
            created_at TEXT NOT NULL,
            provider_mode TEXT NOT NULL CHECK (provider_mode IN ('mock','live')),
            status TEXT NOT NULL CHECK (status IN ('pending','succeeded','failed')),
            failure_code TEXT,
            kind TEXT NOT NULL DEFAULT 'feedback' CHECK (kind IN ('feedback','recommendation')),
            focus TEXT CHECK (focus IN ('slowing_down','surroundings','not_sure')),
            context_json TEXT NOT NULL DEFAULT '{}',
            UNIQUE (session_id, feedback),
            CHECK ((status='failed' AND failure_code IS NOT NULL) OR (status!='failed' AND failure_code IS NULL)),
            CHECK ((kind='feedback' AND session_id IS NOT NULL AND exercise_type IS NOT NULL AND feedback IS NOT NULL AND focus IS NULL)
                OR (kind='recommendation' AND session_id IS NULL AND exercise_type IS NULL AND feedback IS NULL AND focus IS NOT NULL))
        )"""
        connection.execute(conversation_sql)
        connection.execute("""CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY,
            conversation_id TEXT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
            ordinal INTEGER NOT NULL CHECK (ordinal IN (1,2)),
            role TEXT NOT NULL CHECK (role IN ('user','assistant')),
            content TEXT NOT NULL,
            created_at TEXT NOT NULL,
            UNIQUE (conversation_id, ordinal),
            CHECK ((ordinal=1 AND role='user') OR (ordinal=2 AND role='assistant'))
        )""")
        # Version 4 changes only the two exercise enum CHECKs and the planned
        # duration constraint. Copy every column/row unchanged, including STOP
        # history and its message relationships; rollback on any failure.
        for table in ('exercise_sessions', 'conversations'):
            old_sql = connection.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (table,)).fetchone()[0]
            if 'grounding_54321' not in old_sql:
                new_sql = old_sql.replace(table, table + '_v4', 1)
                new_sql = new_sql.replace("'paced_breathing', 'stop'", "'paced_breathing', 'stop', 'grounding_54321'").replace("'paced_breathing','stop'", "'paced_breathing','stop','grounding_54321'")
                if table == 'exercise_sessions':
                    new_sql = new_sql.replace('CHECK (planned_duration_seconds = 60)', "CHECK (planned_duration_seconds = CASE WHEN exercise_type = 'grounding_54321' THEN 70 ELSE 60 END)")
                connection.execute(new_sql)
                connection.execute(f'INSERT INTO {table}_v4 SELECT * FROM {table}')
                connection.execute(f'DROP TABLE {table}')
                connection.execute(f'ALTER TABLE {table}_v4 RENAME TO {table}')
        # v5 reuses conversations/messages for optional recommendations, while
        # preserving every original feedback field and message relationship.
        if 'kind' not in {row[1] for row in connection.execute('PRAGMA table_info(conversations)')}:
            connection.execute(conversation_sql.replace('IF NOT EXISTS conversations', 'conversations_v5', 1))
            old_columns = 'id,app_id,session_id,exercise_type,feedback,created_at,provider_mode,status,failure_code'
            connection.execute(f'INSERT INTO conversations_v5 ({old_columns}) SELECT {old_columns} FROM conversations')
            connection.execute('DROP TABLE conversations')
            connection.execute('ALTER TABLE conversations_v5 RENAME TO conversations')
        # v6 adds nullable summaries only; all original row values remain intact.
        columns = {row[1] for row in connection.execute('PRAGMA table_info(exercise_sessions)')}
        additions = {
            'interaction_mode': "TEXT CHECK (interaction_mode IN ('hold','tap','observe','mixed'))",
            'inhale_interactions': 'INTEGER CHECK (inhale_interactions BETWEEN 0 AND 6)',
            'exhale_interactions': 'INTEGER CHECK (exhale_interactions BETWEEN 0 AND 6)',
            'completed_cycles': 'INTEGER CHECK (completed_cycles BETWEEN 0 AND 6)',
            # v7: nullable active-time summaries preserve every legacy row/column.
            'active_duration_seconds': 'REAL CHECK (active_duration_seconds >= 0)',
            'optional_continuation_seconds': 'REAL CHECK (optional_continuation_seconds >= 0)',
            'active_completed_cycles': 'INTEGER CHECK (active_completed_cycles >= 0)',
        }
        for name, declaration in additions.items():
            if name not in columns:
                connection.execute(f'ALTER TABLE exercise_sessions ADD COLUMN {name} {declaration}')
        if connection.execute('PRAGMA foreign_key_check').fetchone() is not None:
            raise RuntimeError('Migration would violate existing record relationships.')
        # This local app runs a single backend process. A previous in-flight
        # provider call cannot survive its restart, so never invent its reply.
        connection.execute("UPDATE conversations SET status='failed', failure_code='interrupted' WHERE status='pending'")
        connection.execute(
            "INSERT INTO app_metadata (key,value) VALUES (?,?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value WHERE app_metadata.value IN ('1','2','3','4','5','6','7')",
            ("schema_version", "7"),
        )


def database_ready(path: Path) -> bool:
    # mode=ro prevents health requests from creating missing databases.
    with closing(sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True, timeout=3)) as connection:
        return connection.execute(
            "SELECT value FROM app_metadata WHERE key = ?", ("schema_version",)
        ).fetchone() == ("7",)
