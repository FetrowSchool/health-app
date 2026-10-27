-- Open data/app.sqlite3 read-only. Known fictional IDs only; omit app_id.
PRAGMA query_only = ON;
PRAGMA foreign_key_check;
SELECT id, exercise_type, status, duration_seconds, entry_duration_seconds,
       planned_duration_seconds, feedback, started_at, ended_at
FROM exercise_sessions
WHERE id IN ('8155e4d3-9722-42b2-9900-a0ad278e6d44',
             'c734adb7-c728-4436-93e4-e2bcb25917ec',
             'a377b5dc-0451-43ec-b704-3d781aa54cf4',
             'f524c116-7591-486f-8b38-d6c74d2e6ac7',
             'c40678be-91e3-428b-bb14-9b7c62f94773');
SELECT local_date, mood, created_at FROM daily_mood_checkins
WHERE app_id = (SELECT app_id FROM exercise_sessions
                WHERE id = '8155e4d3-9722-42b2-9900-a0ad278e6d44');
SELECT c.id AS conversation_id, c.kind, c.session_id, c.provider_mode,
       c.status, c.failure_code, m.id AS message_id, m.ordinal, m.role,
       m.content, m.created_at
FROM conversations c LEFT JOIN messages m ON m.conversation_id = c.id
WHERE c.id IN ('c0b7dc1a-6dbe-4653-b131-8b1df0a7481c',
               '428a0c07-112a-4964-afe5-2940fb3705cb')
   OR c.session_id = 'c734adb7-c728-4436-93e4-e2bcb25917ec'
   OR (c.status = 'failed' AND c.app_id =
       (SELECT app_id FROM exercise_sessions
        WHERE id = '8155e4d3-9722-42b2-9900-a0ad278e6d44'))
ORDER BY c.id, m.ordinal;
