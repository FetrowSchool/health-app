"""Bounded, identity-scoped, read-only activity history; no provider access."""
from .activity_controller import transaction

LABELS = {'paced_breathing': 'Paced Breathing', 'grounding_54321': '5-4-3-2-1 Grounding', 'stop': 'STOP'}


def read_history(path, app_id, limit=20):
    with transaction(path, write=False) as connection:
        sessions = [dict(row) for row in connection.execute(
            """SELECT id,exercise_type,started_at,ended_at,status,
                      CASE WHEN status='started' THEN NULL ELSE duration_seconds END AS duration_seconds,
                      active_duration_seconds,feedback
               FROM exercise_sessions WHERE app_id=? ORDER BY started_at DESC,id DESC LIMIT ?""",
            (str(app_id), limit))]
        conversations = [dict(row) for row in connection.execute(
            """SELECT id,created_at,kind,status,exercise_type,feedback,provider_mode
               FROM conversations WHERE app_id=? ORDER BY created_at DESC,id DESC LIMIT ?""",
            (str(app_id), limit))]
        for row in conversations:
            # A list preview never copies user/assistant text or stored mood/context.
            if row['status'] == 'failed':
                row['preview'] = 'No generated reply was saved.'
            elif row['status'] == 'pending':
                row['preview'] = 'Response pending.'
            elif row['kind'] == 'recommendation':
                row['preview'] = 'Earlier saved exercise suggestion.'
            else:
                row['preview'] = 'Saved feedback after ' + LABELS[row['exercise_type']] + '.'
        recent = connection.execute(
            """SELECT exercise_type FROM exercise_sessions
               WHERE app_id=? AND status='completed' AND exercise_type IN ('paced_breathing','grounding_54321')
               ORDER BY ended_at DESC,id DESC LIMIT 1""", (str(app_id),)).fetchone()
        return {'sessions': sessions, 'conversations': conversations,
                'recent_completed_exercise': recent['exercise_type'] if recent else None}
