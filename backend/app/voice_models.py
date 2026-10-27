"""Strict voice boundary models; SDP is transport data, never instructions."""
import re
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator

MAX_SDP_BYTES = 64 * 1024
MAX_REQUEST_BYTES = 96 * 1024
MAX_RESPONSE_BYTES = 128 * 1024


def validate_sdp(value: str, *, offer: bool) -> str:
    if len(value.encode('utf-8')) > MAX_SDP_BYTES:
        raise ValueError('Invalid SDP')
    if any(ord(char) < 32 and char not in '\r\n\t' or ord(char) == 127 for char in value):
        raise ValueError('Invalid SDP')
    normalized = value.replace('\r\n', '\n')
    if '\r' in normalized:
        raise ValueError('Invalid SDP')
    lines = normalized.rstrip('\n').split('\n')
    if (len(lines) < 8 or lines[0] != 'v=0'
            or any(re.fullmatch(r'[a-z]=[^\n]+', line) is None for line in lines)):
        raise ValueError('Invalid SDP')
    def has(pattern):
        return any(re.fullmatch(pattern, line) is not None for line in lines)
    fingerprint = any(
        re.fullmatch(r'a=fingerprint:sha-' + algorithm + r' (?:[0-9A-Fa-f]{2}:){' + str(size - 1) + r'}[0-9A-Fa-f]{2}', line)
        for algorithm, size in [('256', 32), ('384', 48), ('512', 64)] for line in lines
    )
    if not all([
        has(r'o=\S+ \d+ \d+ IN IP[46] \S+'), has(r's=.+'), has(r't=\d+ \d+'),
        has(r'm=audio \d+(?:/\d+)? UDP/TLS/RTP/SAVPF(?: \d+)+'),
        has(r'm=application \d+ UDP/DTLS/SCTP webrtc-datachannel'),
        has(r'a=ice-ufrag:\S+'), has(r'a=ice-pwd:\S+'),
        fingerprint,
        has(r'a=setup:actpass' if offer else r'a=setup:(?:active|passive)'),
    ]):
        raise ValueError('Invalid SDP')
    # Preserve the SDP bytes/line endings for the peer/provider to negotiate.
    return value


class VoiceOffer(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    sdp: str = Field(min_length=1, max_length=MAX_SDP_BYTES)

    @field_validator('sdp')
    @classmethod
    def valid_offer(cls, value):
        return validate_sdp(value, offer=True)


class VoiceConfigResponse(BaseModel):
    status: Literal['configured', 'unconfigured']
    duration_seconds: int = Field(ge=1, le=300)


class VoiceSessionResponse(BaseModel):
    session_id: str = Field(min_length=1, max_length=256, strict=True)
    sdp: str = Field(min_length=1, max_length=MAX_SDP_BYTES, strict=True)
    duration_seconds: int = Field(ge=1, le=300, strict=True)

    @field_validator('session_id')
    @classmethod
    def valid_id(cls, value):
        if any(ord(char) < 33 or ord(char) > 126 for char in value):
            raise ValueError('Invalid session ID')
        return value

    @field_validator('sdp')
    @classmethod
    def valid_answer(cls, value):
        return validate_sdp(value, offer=False)


class VoiceCloseRequest(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    session_id: str = Field(min_length=1, max_length=256)

    @field_validator('session_id')
    @classmethod
    def valid_id(cls, value):
        return VoiceSessionResponse.valid_id(value)


class VoiceCloseResponse(BaseModel):
    status: Literal['close_requested'] = 'close_requested'
