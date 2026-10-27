"""All conversation writes are owned by application transactions, never models."""
from datetime import datetime, timezone
import json
from uuid import uuid4
from fastapi import HTTPException

from .activity_controller import transaction, find_session
from .feedback_policy import FALLBACK


def timestamp():
    return datetime.now(timezone.utc).isoformat()


def result(connection, conversation_id, app_id):
    row = connection.execute('SELECT * FROM conversations WHERE id=? AND app_id=?', (str(conversation_id),str(app_id))).fetchone()
    if row is None:
        raise HTTPException(404, 'Conversation not found.')
    record = dict(row)
    record.pop('app_id')
    record['context_used'] = json.loads(record.pop('context_json'))
    record['messages'] = [dict(message) for message in connection.execute(
        'SELECT * FROM messages WHERE conversation_id=? ORDER BY ordinal ASC', (record['id'],))]
    record['fallback_message'] = FALLBACK if record['status'] == 'failed' else None
    record['recommendation'] = None
    if record['kind'] == 'recommendation' and record['status'] == 'succeeded':
        record['recommendation'] = json.loads(record['messages'][-1]['content'])
    record['saved'] = True
    return record


def reserve(path, app_id, payload, mode):
    with transaction(path) as connection:
        session = find_session(connection, payload.session_id, app_id)
        if session['status'] != 'completed' or session['exercise_type'] != payload.exercise_type:
            raise HTTPException(409, 'Feedback response requires the matching completed exercise.')
        by_id = connection.execute('SELECT * FROM conversations WHERE id=?', (str(payload.request_id),)).fetchone()
        if by_id is not None and (by_id['kind'],by_id['app_id'],by_id['session_id'],by_id['feedback']) != ('feedback',str(app_id),str(payload.session_id),payload.feedback):
            raise HTTPException(409, 'Request ID already belongs to a different exchange.')
        existing = connection.execute('SELECT id FROM conversations WHERE session_id=? AND feedback=?', (str(payload.session_id),payload.feedback)).fetchone()
        if existing:
            return result(connection, existing['id'], app_id), False
        created = timestamp()
        context = limited_context(connection, app_id, payload.local_date)
        connection.execute('INSERT INTO conversations (id,app_id,session_id,exercise_type,feedback,created_at,provider_mode,status,context_json) VALUES (?,?,?,?,?,?,?,?,?)',
                           (str(payload.request_id),str(app_id),str(payload.session_id),payload.exercise_type,payload.feedback,created,mode,'pending',json.dumps(context)))
        connection.execute('INSERT INTO messages VALUES (?,?,?,?,?,?)',
                           (str(uuid4()),str(payload.request_id),1,'user',payload.user_message,created))
        return result(connection,payload.request_id,app_id), True


def finalize(path, app_id, conversation_id, text=None, failure_code=None):
    with transaction(path) as connection:
        record = result(connection,conversation_id,app_id)
        if record['status'] != 'pending':
            return record
        if failure_code:
            connection.execute("UPDATE conversations SET status='failed',failure_code=? WHERE id=? AND app_id=?",(failure_code,str(conversation_id),str(app_id)))
        else:
            connection.execute('INSERT INTO messages VALUES (?,?,?,?,?,?)',
                               (str(uuid4()),str(conversation_id),2,'assistant',text,timestamp()))
            connection.execute("UPDATE conversations SET status='succeeded' WHERE id=? AND app_id=?",(str(conversation_id),str(app_id)))
        return result(connection,conversation_id,app_id)


def retrieve(path, app_id, conversation_id):
    with transaction(path, write=False) as connection:
        return result(connection,conversation_id,app_id)


def limited_context(connection, app_id, local_date):
    mood = None
    if local_date is not None:
        row = connection.execute('SELECT mood FROM daily_mood_checkins WHERE app_id=? AND local_date=?', (str(app_id),local_date.isoformat())).fetchone()
        if row and row['mood'] != 'skipped': mood = row['mood']
    rows = connection.execute("SELECT exercise_type,status,feedback FROM exercise_sessions WHERE app_id=? AND exercise_type IN ('paced_breathing','grounding_54321') AND status IN ('completed','exited') ORDER BY started_at DESC,id DESC LIMIT 3", (str(app_id),)).fetchall()
    return {'local_date': local_date.isoformat() if local_date else None, 'mood': mood, 'recent': [dict(row) for row in rows]}

