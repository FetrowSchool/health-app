"""Bounded Live requests with opt-in sanitized diagnostics; no SDK, retries or database access."""
import asyncio
from contextlib import asynccontextmanager
from copy import deepcopy
import json
import hashlib
import logging
import time
from urllib.parse import quote
import httpx
from .voice_models import MAX_RESPONSE_BYTES, VoiceSessionResponse
from pathlib import Path

VOICE_ENDPOINT = 'https://api.openai.com/v1/live/sessions'
VOICE_MODEL = 'gpt-live-1'
SESSION_CONFIG_PATH = Path(__file__).with_name('voice_session.json')
logger = logging.getLogger('pause.voice.diagnostics')
prompt_logger = logging.getLogger('pause.voice.prompts')
# Only these fixed classifications may enter opt-in development logs.
ERROR_CATEGORIES = {
    'invalid_api_key': 'authentication', 'authentication_error': 'authentication',
    'insufficient_quota': 'credits_or_quota', 'billing_hard_limit_reached': 'credits_or_quota',
    'model_not_found': 'model_access', 'permission_denied': 'access_denied',
    'invalid_request_error': 'invalid_request', 'invalid_value': 'invalid_request',
    'unsupported_parameter': 'unsupported_setting', 'rate_limit_exceeded': 'rate_limit',
}


def error_category(status, data):
    error = data.get('error') if isinstance(data, dict) else None
    if isinstance(error, dict):
        for field in ('code', 'type'):
            value = error.get(field)
            if isinstance(value, str) and value in ERROR_CATEGORIES:
                return ERROR_CATEGORIES[value]
    return {401: 'authentication', 403: 'access_denied', 404: 'not_found',
            400: 'invalid_request', 422: 'invalid_request', 429: 'rate_limit_or_quota'}.get(status, 'provider_http_error')




class VoiceFailure(Exception):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


def strict_json(value):
    def pairs(items):
        result = {}
        for key, item in items:
            if key in result:
                raise ValueError('Duplicate field')
            result[key] = item
        return result
    def constant(_):
        raise ValueError('Invalid JSON constant')
    return json.loads(value, object_pairs_hook=pairs, parse_constant=constant)


class VoiceProvider:
    def __init__(self, settings, transport=None, *, session_config=None, client=None, config_label=None):
        self.settings = settings
        self.transport = transport
        # Snapshot server-owned JSON outside the timed asynchronous request.
        self.session_config = deepcopy(session_config) if session_config is not None else strict_json(SESSION_CONFIG_PATH.read_text())
        self.client = client
        self.config_source = (SESSION_CONFIG_PATH.name if session_config is None else
                              'voice_diagnostic.py' if config_label == 'diagnostic' else 'server_override')
        self._prompt_diagnostic('loaded', self.session_config)
        # Local-prototype allowlist only; no audio/transcripts or durable records.
        self.issued = {}
        self.pending_creates = 0

    def _prompt_diagnostic(self, phase, session):
        if not self.settings.voice_diagnostics:
            return
        live = session.get('instructions') or ''
        backend = (session.get('delegation') or {}).get('responses', {}).get('instructions') or ''
        # These are server-owned strings. Never log their contents or request data.
        def fingerprint(value):
            return hashlib.sha256(value.encode('utf-8')).hexdigest() if value else 'absent'
        prompt_logger.warning('voice_prompt phase=%s source=%s live_hash=%s live_chars=%s included=%s backend_hash=%s backend_chars=%s',
                              phase, self.config_source, fingerprint(live), len(live), bool(live.strip()),
                              fingerprint(backend), len(backend))

    def _diagnose(self, trace):
        if self.settings.voice_diagnostics:
            # No exception text, headers, key, body, SDP, IDs or transcript content.
            logger.warning('voice_create stage=%s upstream_status=%s category=%s phase=%s timeout_kind=%s elapsed_ms=%s',
                           trace['stage'], trace['status'], trace['category'], trace['phase'],
                           trace['timeout_kind'], round((time.monotonic()-trace['started'])*1000))

    async def create(self, offer):
        if not self.settings.voice_configured:
            raise VoiceFailure('unconfigured')
        self._prune()
        if len(self.issued) + self.pending_creates >= 256:
            raise VoiceFailure('provider_error')
        self.pending_creates += 1
        trace = {'stage': 'session_config', 'status': None, 'category': 'internal_error',
                 'phase': 'not_started', 'timeout_kind': 'none', 'started': time.monotonic()}
        try:
            result = await asyncio.wait_for(self._create(offer, trace), self.settings.voice_timeout_seconds)
            trace.update(stage='session_created', category='success')
            self._diagnose(trace)
            self.issued[result.session_id] = {'expires': time.monotonic() + 900, 'close_task': None}
            return result
        except (TimeoutError, httpx.TimeoutException) as error:
            trace['timeout_kind'] = ('os_timeout' if getattr(error, 'errno', None) is not None else
                {httpx.ConnectTimeout: 'connect', httpx.WriteTimeout: 'write',
                 httpx.ReadTimeout: 'read', httpx.PoolTimeout: 'pool'}.get(type(error), 'total'))
            trace['category'] = 'timeout'
            self._diagnose(trace)
            raise VoiceFailure('timeout') from None
        except httpx.TransportError:
            trace['category'] = 'transport_error'
            self._diagnose(trace)
            raise VoiceFailure('provider_error') from None
        except Exception:
            self._diagnose(trace)
            # Never forward provider response bodies, input, headers or exceptions.
            raise VoiceFailure('provider_error') from None
        finally:
            self.pending_creates -= 1

    def _prune(self):
        for sid, item in list(self.issued.items()):
            if item['expires'] < time.monotonic() and (item['close_task'] is None or item['close_task'].done()):
                del self.issued[sid]

    async def close(self, session_id):
        self._prune()
        item = self.issued.get(session_id)
        if item is None:
            raise VoiceFailure('unknown_session')
        if item['close_task'] is None:
            item['close_task'] = asyncio.create_task(self._close(session_id))
        # Concurrent/repeated requests share the same bounded operation, including failure.
        await asyncio.shield(item['close_task'])

    async def _close(self, session_id):
        try:
            await asyncio.wait_for(self._hangup(session_id), min(3, self.settings.voice_timeout_seconds))
        except (TimeoutError, httpx.TimeoutException):
            raise VoiceFailure('timeout') from None
        except Exception:
            raise VoiceFailure('provider_error') from None

    @asynccontextmanager
    async def _http_client(self):
        if self.client is not None:
            yield self.client
        else:
            transport = self.transport if self.transport is not None else httpx.AsyncHTTPTransport(retries=0)
            async with httpx.AsyncClient(transport=transport, trust_env=False, follow_redirects=False,
                    timeout=httpx.Timeout(self.settings.voice_timeout_seconds,
                                          connect=min(3, self.settings.voice_timeout_seconds))) as client:
                yield client

    async def _hangup(self, session_id):
        timeout = min(3, self.settings.voice_timeout_seconds)
        async with self._http_client() as client:
            async with client.stream('POST', VOICE_ENDPOINT + '/' + quote(session_id, safe='') + '/hangup',
                                     timeout=timeout,
                                     headers={'Authorization': 'Bearer ' + self.settings.voice_api_key.strip()}) as response:
                if response.status_code not in (200, 204):
                    raise ValueError('Hangup not accepted')

    async def _create(self, offer, trace):
        payload = {
            'session': deepcopy(self.session_config),
            'transport': {'type': 'webrtc', 'sdp': offer.sdp},
        }
        self._prompt_diagnostic('outgoing', payload['session'])
        trace.update(stage='provider_request', category='transport_error', phase='client_setup')
        async def http_trace(event, _info):
            # Ignore trace metadata entirely: it can contain headers and transport data.
            phases = {'connect_tcp.started': 'connecting', 'connect_tcp.complete': 'connected',
                      'start_tls.started': 'tls_connecting', 'start_tls.complete': 'tls_connected',
                      'send_request_headers.complete': 'headers_sent',
                      'send_request_body.started': 'body_sending', 'send_request_body.complete': 'body_sent',
                      'receive_response_headers.started': 'awaiting_headers',
                      'receive_response_headers.complete': 'headers_received',
                      'receive_response_body.started': 'body_receiving', 'receive_response_body.complete': 'body_received'}
            suffix = event.split('.', 1)[-1]
            if suffix in phases:
                trace['phase'] = phases[suffix]
        async with self._http_client() as client:
            trace['phase'] = 'transport_ready'
            async with client.stream('POST', VOICE_ENDPOINT,
                                     headers={'Authorization': 'Bearer ' + self.settings.voice_api_key.strip()},
                                     json=payload, extensions={'trace': http_trace}) as response:
                trace.update(stage='provider_response', status=response.status_code, category='malformed_response')
                data = bytearray()
                async for chunk in response.aiter_bytes():
                    data.extend(chunk)
                    if len(data) > MAX_RESPONSE_BYTES:
                        raise ValueError('Oversized provider response')
                if response.status_code != 201:
                    try:
                        body = strict_json(data)
                    except (ValueError, UnicodeError, RecursionError):
                        body = None
                    trace['category'] = error_category(response.status_code, body)
                    raise ValueError('Provider request rejected')
                if response.headers.get('content-type', '').split(';')[0].strip().lower() != 'application/json':
                    raise ValueError('Invalid provider response')
                result = strict_json(data)
                if not isinstance(result, dict) or not isinstance(result.get('session'), dict) or not isinstance(result.get('transport'), dict):
                    raise ValueError('Invalid provider response')
                if result['transport'].get('type') != 'webrtc':
                    raise ValueError('Unexpected transport')
                trace.update(stage='answer_validation', category='malformed_answer')
                return VoiceSessionResponse(
                    session_id=result['session']['id'], sdp=result['transport']['sdp'],
                    duration_seconds=self.settings.voice_duration_seconds,
                )
