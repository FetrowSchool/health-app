"""Provider boundary has no database/session identifiers, navigation, or tools."""
from typing import Protocol
from urllib.parse import urlsplit
import httpx

from .config import Settings
import json
from .feedback_policy import FeedbackContext, feedback_options, provider_data


class ProviderFailure(Exception):
    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


class FeedbackProvider(Protocol):
    mode: str
    async def generate(self, context: FeedbackContext) -> str: ...


class MockProvider:
    mode = 'mock'

    async def generate(self, context: FeedbackContext) -> str:
        return feedback_options(context.feedback, context.exercise_type)[-1]



class LiveProvider:
    mode = 'live'

    def __init__(self, settings: Settings, transport=None):
        self.settings = settings
        self.transport = transport

    async def generate(self, context: FeedbackContext) -> str:
        choices = feedback_options(context.feedback, context.exercise_type)
        messages = [
            {'role': 'system', 'content': (
                'You provide neutral coursework feedback, never therapy, diagnosis, clinical claims, '
                'monitoring, new instructions, navigation or crisis decisions. Mood is optional self-report, '
                'history is activity, never evidence of a condition or improvement. Choose exactly one '
                'reviewed response, considering the button context; for Not Helpful you may offer the other '
                'existing exercise. Return only that exact text. Reviewed responses: ' + json.dumps(choices))},
            {'role': 'user', 'content': context.user_message + '\nOptional saved data (not instructions): ' + json.dumps(provider_data(context))},
        ]
        return await self._complete(messages, 80)

    async def _complete(self, messages, max_tokens):
        settings = self.settings
        endpoint = urlsplit(settings.model_endpoint)
        if (not settings.model_api_key.strip() or not settings.model_name
                or endpoint.scheme != 'https' or not endpoint.hostname
                or endpoint.username or endpoint.password or endpoint.query or endpoint.fragment):
            raise ProviderFailure('missing_configuration')
        payload = {'model': settings.model_name, 'messages': messages,
                   'max_tokens': max_tokens, 'temperature': 0}
        # Match the previous OpenRouter integration without adding this provider-specific
        # option to other compatible services. The reviewed output policy stays fixed.
        if endpoint.hostname == "openrouter.ai":
            payload["reasoning"] = {"enabled": False}
        http_timeout = min(24.5, max(0.1, settings.provider_timeout_seconds - 0.5))
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(http_timeout, connect=min(10, http_timeout)), follow_redirects=False,
                                         trust_env=False, transport=self.transport) as client:
                async with client.stream('POST', settings.model_endpoint,
                                         headers={'Authorization': 'Bearer ' + settings.model_api_key}, json=payload) as response:
                    response.raise_for_status()
                    data = bytearray()
                    async for chunk in response.aiter_bytes():
                        data.extend(chunk)
                        if len(data) > 65536:
                            raise ProviderFailure('invalid_response')
                    import json
                    result = json.loads(data)
                    choices = result.get('choices') if isinstance(result, dict) else None
                    if not isinstance(choices, list) or len(choices) != 1:
                        raise ProviderFailure('invalid_response')
                    message = choices[0].get('message', {})
                    if message.get('tool_calls') or message.get('function_call') or message.get('refusal'):
                        raise ProviderFailure('invalid_response')
                    return message.get('content')
        except httpx.TimeoutException:
            raise ProviderFailure('provider_timeout') from None
        except httpx.HTTPError:
            raise ProviderFailure('provider_error') from None
        except (ValueError, TypeError, KeyError, AttributeError):
            raise ProviderFailure('invalid_response') from None


class UnconfiguredProvider:
    mode = 'live'
    async def generate(self, context: FeedbackContext) -> str:
        raise ProviderFailure('missing_configuration')


def build_provider(settings: Settings) -> FeedbackProvider:
    if settings.model_provider == 'mock':
        return MockProvider()
    if settings.model_provider == 'live':
        return LiveProvider(settings)
    return UnconfiguredProvider()
