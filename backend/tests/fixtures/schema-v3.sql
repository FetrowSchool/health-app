CREATE TABLE exercise_sessions (
            id TEXT PRIMARY KEY,
            app_id TEXT NOT NULL,
            exercise_type TEXT NOT NULL CHECK (exercise_type IN ('paced_breathing', 'stop')),
            started_at TEXT NOT NULL,
            ended_at TEXT,
            status TEXT NOT NULL DEFAULT 'started' CHECK (status IN ('started', 'completed', 'exited')),
            duration_seconds REAL NOT NULL DEFAULT 0 CHECK (duration_seconds >= 0),
            entry_duration_seconds REAL NOT NULL CHECK (entry_duration_seconds >= 0),
            planned_duration_seconds INTEGER NOT NULL DEFAULT 60 CHECK (planned_duration_seconds = 60),
            feedback TEXT CHECK (feedback IN ('helpful', 'not_helpful', 'skipped')),
            CHECK ((status = 'started' AND ended_at IS NULL AND duration_seconds = 0)
                OR (status != 'started' AND ended_at IS NOT NULL)),
            CHECK (feedback IS NULL OR status = 'completed')
        );
CREATE TABLE conversations (
            id TEXT PRIMARY KEY,
            app_id TEXT NOT NULL,
            session_id TEXT NOT NULL REFERENCES exercise_sessions(id) ON DELETE CASCADE,
            exercise_type TEXT NOT NULL CHECK (exercise_type IN ('paced_breathing','stop')),
            feedback TEXT NOT NULL CHECK (feedback IN ('helpful','not_helpful')),
            created_at TEXT NOT NULL,
            provider_mode TEXT NOT NULL CHECK (provider_mode IN ('mock','live')),
            status TEXT NOT NULL CHECK (status IN ('pending','succeeded','failed')),
            failure_code TEXT,
            UNIQUE (session_id, feedback),
            CHECK ((status='failed' AND failure_code IS NOT NULL) OR (status!='failed' AND failure_code IS NULL))
        );
CREATE TABLE messages (
            id TEXT PRIMARY KEY,
            conversation_id TEXT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
            ordinal INTEGER NOT NULL CHECK (ordinal IN (1,2)),
            role TEXT NOT NULL CHECK (role IN ('user','assistant')),
            content TEXT NOT NULL,
            created_at TEXT NOT NULL,
            UNIQUE (conversation_id, ordinal),
            CHECK ((ordinal=1 AND role='user') OR (ordinal=2 AND role='assistant'))
        );
CREATE TABLE daily_mood_checkins (
            app_id TEXT NOT NULL,
            local_date TEXT NOT NULL,
            mood TEXT NOT NULL CHECK (mood IN ('calm','okay','anxious','overwhelmed','skipped')),
            created_at TEXT NOT NULL,
            PRIMARY KEY (app_id, local_date)
        );
CREATE TABLE app_metadata (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );