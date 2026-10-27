from typing import Literal
from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: Literal["ok"]
    database: Literal["ready"]
    model_configured: bool

from datetime import date
from uuid import UUID
from pydantic import AwareDatetime, ConfigDict, Field, model_validator


class WriteModel(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


class SessionStart(WriteModel):
    id: UUID
    exercise_type: Literal["paced_breathing", "stop", "grounding_54321"]
    started_at: AwareDatetime
    entry_duration_seconds: float = Field(ge=0, le=31536000)


class BreathingMetrics(WriteModel):
    active_duration_seconds: float | None = Field(default=None, ge=0, le=31536000)
    optional_continuation_seconds: float | None = Field(default=None, ge=0, le=31536000)
    active_completed_cycles: int | None = Field(default=None, ge=0, le=3153600, strict=True)
    interaction_mode: Literal['hold', 'tap', 'observe', 'mixed'] | None = None
    inhale_interactions: int | None = Field(default=None, ge=0, le=6, strict=True)
    exhale_interactions: int | None = Field(default=None, ge=0, le=6, strict=True)
    completed_cycles: int | None = Field(default=None, ge=0, le=6, strict=True)

    @model_validator(mode='after')
    def complete_metrics(self):
        values = [self.interaction_mode, self.inhale_interactions, self.exhale_interactions, self.completed_cycles]
        if any(v is not None for v in values) and any(v is None for v in values):
            raise ValueError('Interaction summary must be complete or omitted.')
        timing = [self.active_duration_seconds, self.optional_continuation_seconds, self.active_completed_cycles]
        if any(v is not None for v in timing):
            if any(v is None for v in timing) or any(v is not None for v in values):
                raise ValueError('Active timing must be complete and separate from legacy interaction metrics.')
        if self.interaction_mode == 'observe' and (self.inhale_interactions or self.exhale_interactions):
            raise ValueError('Observation mode has no detected interactions.')
        return self


class SessionEnd(BreathingMetrics):
    status: Literal["completed", "exited"]
    ended_at: AwareDatetime
    duration_seconds: float = Field(ge=0, le=31536000)


class FeedbackInput(WriteModel):
    feedback: Literal["helpful", "not_helpful", "skipped"]


class SessionResponse(BreathingMetrics):
    id: UUID
    app_id: UUID
    exercise_type: Literal["paced_breathing", "stop", "grounding_54321"]
    started_at: AwareDatetime
    ended_at: AwareDatetime | None
    status: Literal["started", "completed", "exited"]
    duration_seconds: float
    entry_duration_seconds: float
    planned_duration_seconds: int
    feedback: Literal["helpful", "not_helpful", "skipped"] | None


class MoodInput(WriteModel):
    mood: Literal["calm", "okay", "anxious", "overwhelmed", "skipped"]


class MoodResponse(BaseModel):
    app_id: UUID
    local_date: date
    mood: Literal["calm", "okay", "anxious", "overwhelmed", "skipped"]
    created_at: AwareDatetime

from pydantic import model_validator
from .feedback_policy import predefined_message


class FeedbackRequest(WriteModel):
    request_id: UUID
    session_id: UUID
    exercise_type: Literal['paced_breathing', 'stop', 'grounding_54321']
    feedback: Literal['helpful', 'not_helpful']
    user_message: str = Field(max_length=160)
    local_date: date | None = None

    @model_validator(mode='after')
    def only_button_messages(self):
        if self.user_message != predefined_message(self.exercise_type, self.feedback):
            raise ValueError('Only the predefined feedback-button message is accepted.')
        return self


class MessageResponse(BaseModel):
    id: UUID
    conversation_id: UUID
    ordinal: int
    role: Literal['user', 'assistant']
    content: str
    created_at: AwareDatetime


class RecommendationResult(WriteModel):
    """Read-only response shape for preserved historical recommendations."""
    exercise_id: Literal['paced_breathing', 'grounding_54321']
    short_reason: str = Field(min_length=1, max_length=140)


class ConversationResponse(BaseModel):
    id: UUID
    session_id: UUID | None
    exercise_type: Literal['paced_breathing', 'stop', 'grounding_54321'] | None
    feedback: Literal['helpful', 'not_helpful'] | None
    created_at: AwareDatetime
    provider_mode: Literal['mock', 'live']
    status: Literal['pending', 'succeeded', 'failed']
    failure_code: Literal['missing_configuration', 'provider_timeout', 'provider_error', 'invalid_response', 'interrupted'] | None
    messages: list[MessageResponse]
    fallback_message: str | None
    saved: bool = True

    kind: Literal['feedback', 'recommendation'] = 'feedback'
    focus: Literal['slowing_down', 'surroundings', 'not_sure'] | None = None
    context_used: dict = Field(default_factory=dict)
    recommendation: RecommendationResult | None = None

