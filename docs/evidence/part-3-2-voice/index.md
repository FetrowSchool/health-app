# Optional voice frontend evidence — October 26, 2026

[Closed voice panel,390×844, keyboard focus](01-voice-closed-390x844.png): actual running Vue interface in the browser. All three text choices, microphone, Return Home and Crisis Support were present/enabled; no microphone was selected. Screenshot dimensions independently confirmed390×844.

DOM measurements: width390, horizontal scroll width390, total content height927. Text/microphone/Home buttons56px; safety button44px. Return Home bottom809px fits844. Footer uses vertical scrolling. Microphone keyboard focus had a3px solid outline. Crisis Support opened and returned Home without any model request or operating resource links.

Transport/state evidence is **mocked**, not a live audio demonstration: `cd frontend && node --test tests/voice.test.js` passed19 checks with fake MediaDevices, peer, channel, audio, clock and API. Permission/connecting/active/muted/closing/closed/error, ICE ordering, autoplay rejection/retry, late events, cancellation, duration and resource release are covered. Raw transcripts are ignored, never retained in UI state or persisted. Existing frontend regression tests also pass; see [verification](../../verification.md) for complete results/build status.

No real device permission, audio capture/playback, SDP negotiation, provider connection, transcript retention or live-model safety test was performed. Permission/active/muted/error states have not been visually reviewed in a real browser. Those require a separate mocked UI harness or later authorized device/provider verification; unit transport state coverage is not rendered state evidence. No paid calls or sensitive scenarios.

Lifecycle refinement, October26:33 focused frontend voice checks (69 total frontend) and27 backend voice checks passed using browser/API/provider fakes and temporary SQLite only. Coverage now includes750ms End acknowledgement/timeout, repeated actions, late SDP hangup without stale UI, fresh starts and unmount/navigation/Crisis Support/pagehide/hidden/duration cleanup. The screenshot above is the prior Closed-state layout and predates the explicit mute/billing notice; no updated rendered-state evidence is claimed. See the newest verification entry for the resumed run, build status and provider closure limits.

Failure investigation, later October26:

- [Microphone-only diagnostic pending](02-microphone-only-pending.png): same-origin actual browser feature checks are true; getUserMedia was invoked but did not resolve/reject or show a visible permission prompt. No provider, recording or transmission code; temporary page/tab removed afterward. Hardware/permission success is unverified.
- [Restarted application explicitly unconfigured](03-runtime-unconfigured.png): corrected backend routes now answer200, but OpenAI key and delegated model are missing. This configuration gate prevents the app from reaching microphone/SDP/provider stages. Text controls and independent support remain available. No live response is shown.

Full findings, sanitized logs, unchanged SQLite digests and27 backend/70 frontend test results are in [actual failure verification](../../verification.md#actual-voice-failure-investigation). Original route404 was fixed by restarting the stale backend, with existing offloaded dependency hydration; no application code, credentials or packages changed. The earlier instruction to restart because routes were absent is superseded by this investigation.


- [Exact handoff idle interface](04-exact-handoff-idle.png): actual browser Closed state with text choices and updated temporary-transcript notice. No live microphone/provider session; transcript timing/finalization evidence is mocked.

- [Approved attempt result](approved-attempt.json) and [browser timeout screenshot](05-approved-attempt-timeout.png): one native-SDP session request without microphone capture, backend provider_request/timeout/no upstream status. Not a successful live conversation; prior502 not reproduced.

- [Isolated diagnostic evidence](minimal-diagnostic.json) and [microphone-only result](06-minimal-microphone-check.png): actual microphone access/release, no paid request; minimal WebRTC lifecycle uses mocks.

- [Personality prompt delivery evidence](prompt-delivery.json): non-sensitive prompt hashes/lengths and mocked outgoing-request verification; no live behavioral audition.
