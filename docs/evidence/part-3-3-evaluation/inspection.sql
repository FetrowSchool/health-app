-- Read-only inspection of the isolated fictional evaluation.sqlite3 only.
-- Open using mode=ro. No application identity, credentials or raw voice data.
SELECT id, exercise_type, status, started_at, ended_at, duration_seconds,
       active_duration_seconds, feedback
FROM exercise_sessions ORDER BY started_at DESC, id DESC;
SELECT local_date, mood FROM daily_mood_checkins ORDER BY local_date;
SELECT c.id, c.kind, c.session_id, c.provider_mode, c.status,
       s.exercise_type, s.status AS session_status
FROM conversations c LEFT JOIN exercise_sessions s ON s.id=c.session_id
ORDER BY c.created_at, c.id;
SELECT id, conversation_id, ordinal, role, content, created_at
FROM messages ORDER BY conversation_id, ordinal, id;
PRAGMA foreign_key_check;
