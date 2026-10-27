"""Reviewed product copy, not therapeutic guidance or clinical assessment."""
from dataclasses import dataclass

FALLBACK = "No generated response is available. You can return home whenever you choose."
APPROVED_RESPONSES = {
    "helpful": "Feedback noted. You can return home whenever you choose.",
    "not_helpful": "Feedback noted. You can stop here or return home whenever you choose.",
}
EXERCISE_LABELS = {"paced_breathing": "Paced Breathing", "stop": "STOP", "grounding_54321": "5-4-3-2-1 Grounding"}
FEEDBACK_LABELS = {"helpful": "Helpful", "not_helpful": "Not Helpful"}


def predefined_message(exercise: str, feedback: str) -> str:
    return f"I selected {FEEDBACK_LABELS[feedback]} after the {EXERCISE_LABELS[exercise]} exercise."


def feedback_options(feedback, exercise=None):
    choices = [APPROVED_RESPONSES[feedback]]
    if feedback == 'helpful':
        choices.append('Feedback noted. You can choose what to do next.')
    elif exercise in ('paced_breathing', 'grounding_54321'):
        other = '5-4-3-2-1 Grounding' if exercise == 'paced_breathing' else 'Paced Breathing'
        choices.append(f'Feedback noted. You can try {other} or return home whenever you choose.')
    return choices


def accepted_response(value, feedback, exercise=None) -> bool:
    return (isinstance(value, str) and len(value) <= 240 and len(value.split()) <= 40
            and value in feedback_options(feedback, exercise))


@dataclass(frozen=True)
class FeedbackContext:
    exercise_type: str
    feedback: str
    user_message: str
    mood: str | None = None
    recent: tuple = ()


def provider_data(context: FeedbackContext):
    # Preserve the existing bounded feedback payload; no identities or timestamps.
    return {'mood': context.mood, 'recent': list(context.recent),
            'exercise_type': context.exercise_type, 'feedback': context.feedback}
