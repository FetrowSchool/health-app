"""Transactional application-owned writes; no model access or user accounts."""
from contextlib import contextmanager, closing
from datetime import date, datetime, timezone
from pathlib import Path
import sqlite3
from uuid import UUID
from fastapi import HTTPException

from .models import SessionStart, SessionEnd


@contextmanager
def transaction(path: Path, write: bool = True):
    try:
        # rw avoids silently creating an empty DB after a file/storage failure.
        mode = "rw" if write else "ro"
        with closing(sqlite3.connect(path.resolve().as_uri() + "?mode=" + mode, uri=True, timeout=3)) as connection:
            connection.row_factory = sqlite3.Row
            connection.execute("PRAGMA foreign_keys = ON")
            with connection:
                if write:
                    connection.execute("BEGIN IMMEDIATE")
                yield connection
    except sqlite3.Error:
        raise HTTPException(503, "Local data could not be saved or loaded.") from None


def utc(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat()


def find_session(connection, session_id: UUID, app_id: UUID):
    row = connection.execute(
        "SELECT * FROM exercise_sessions WHERE id=? AND app_id=?", (str(session_id), str(app_id))
    ).fetchone()
    if row is None:
        raise HTTPException(404, "Session not found.")
    return dict(row)


def start_session(path: Path, app_id: UUID, payload: SessionStart):
    with transaction(path) as connection:
        row = connection.execute("SELECT * FROM exercise_sessions WHERE id=?", (str(payload.id),)).fetchone()
        expected = (str(app_id), payload.exercise_type, utc(payload.started_at), payload.entry_duration_seconds)
        if row is not None:
            if (row['app_id'], row['exercise_type'], row['started_at'], row['entry_duration_seconds']) != expected:
                raise HTTPException(409, "Session ID already belongs to a different start request.")
            return dict(row)
        connection.execute(
            "INSERT INTO exercise_sessions (id,app_id,exercise_type,started_at,entry_duration_seconds,planned_duration_seconds) VALUES (?,?,?,?,?,?)",
            (str(payload.id), *expected, 70 if payload.exercise_type == "grounding_54321" else 60),
        )
        return find_session(connection, payload.id, app_id)


def read_session(path: Path, app_id: UUID, session_id: UUID):
    with transaction(path, write=False) as connection:
        return find_session(connection, session_id, app_id)


def end_session(path: Path, app_id: UUID, session_id: UUID, payload: SessionEnd):
    with transaction(path) as connection:
        row = find_session(connection, session_id, app_id)
        if payload.ended_at < datetime.fromisoformat(row['started_at']):
            raise HTTPException(422, "End timestamp must not precede the start.")
        if payload.status == 'completed' and row['exercise_type'] == 'paced_breathing' and payload.active_duration_seconds is None and payload.duration_seconds < 60:
            raise HTTPException(422, "Breathing completion requires all six cycles.")
        wall_elapsed = (payload.ended_at - datetime.fromisoformat(row['started_at'])).total_seconds()
        if abs(wall_elapsed - payload.duration_seconds) > 1:
            raise HTTPException(422, "End timestamp and measured duration do not agree.")
        timing = (payload.active_duration_seconds, payload.optional_continuation_seconds, payload.active_completed_cycles)
        if payload.active_duration_seconds is not None:
            active = payload.active_duration_seconds
            if row['exercise_type'] != 'paced_breathing':
                raise HTTPException(422, 'Active timing is only supported for breathing.')
            if active > payload.duration_seconds + 0.001:
                raise HTTPException(422, 'Active duration cannot exceed wall duration.')
            if (abs(payload.optional_continuation_seconds - max(0, active - 60)) > 0.001
                    or payload.active_completed_cycles != int(active // 10)):
                raise HTTPException(422, 'Active timing summary does not agree with elapsed active time.')
        metrics = (payload.interaction_mode, payload.inhale_interactions, payload.exhale_interactions, payload.completed_cycles)
        if payload.interaction_mode is not None:
            if row['exercise_type'] != 'paced_breathing':
                raise HTTPException(422, "Interaction summary is only supported for breathing.")
            cycles = min(6, int(payload.duration_seconds // 10))
            inhales = min(6, int(payload.duration_seconds // 10) + 1)
            exhales = min(6, int((payload.duration_seconds + 6) // 10))
            if payload.completed_cycles != cycles or payload.inhale_interactions > inhales or payload.exhale_interactions > exhales:
                raise HTTPException(422, "Interaction summary exceeds elapsed exercise phases.")
        final = (payload.status, utc(payload.ended_at), payload.duration_seconds, *metrics, *timing)
        if row['status'] != 'started':
            if (row['status'], row['ended_at'], row['duration_seconds'], row['interaction_mode'], row['inhale_interactions'], row['exhale_interactions'], row['completed_cycles'], row['active_duration_seconds'], row['optional_continuation_seconds'], row['active_completed_cycles']) != final:
                raise HTTPException(409, "Finished session cannot be overwritten.")
            return row
        connection.execute(
            "UPDATE exercise_sessions SET status=?, ended_at=?, duration_seconds=?, interaction_mode=?, inhale_interactions=?, exhale_interactions=?, completed_cycles=?, active_duration_seconds=?, optional_continuation_seconds=?, active_completed_cycles=? WHERE id=? AND app_id=? AND status='started'",
            (*final, str(session_id), str(app_id)),
        )
        return find_session(connection, session_id, app_id)


def save_feedback(path: Path, app_id: UUID, session_id: UUID, feedback: str):
    with transaction(path) as connection:
        row = find_session(connection, session_id, app_id)
        if row['status'] != 'completed':
            raise HTTPException(409, "Feedback is available only after completion.")
        connection.execute("UPDATE exercise_sessions SET feedback=? WHERE id=? AND app_id=?", (feedback, str(session_id), str(app_id)))
        return find_session(connection, session_id, app_id)


def read_mood(path: Path, app_id: UUID, day: date):
    with transaction(path, write=False) as connection:
        row = connection.execute("SELECT * FROM daily_mood_checkins WHERE app_id=? AND local_date=?", (str(app_id), day.isoformat())).fetchone()
        if row is None:
            raise HTTPException(404, "Check-in not found.")
        return dict(row)


def save_mood(path: Path, app_id: UUID, day: date, mood: str):
    with transaction(path) as connection:
        row = connection.execute("SELECT * FROM daily_mood_checkins WHERE app_id=? AND local_date=?", (str(app_id), day.isoformat())).fetchone()
        if row is not None:
            if row['mood'] != mood:
                raise HTTPException(409, "This local day already has a check-in.")
            return dict(row)
        created = utc(datetime.now(timezone.utc))
        connection.execute("INSERT INTO daily_mood_checkins VALUES (?,?,?,?)", (str(app_id), day.isoformat(), mood, created))
        return dict(app_id=str(app_id), local_date=day.isoformat(), mood=mood, created_at=created)
