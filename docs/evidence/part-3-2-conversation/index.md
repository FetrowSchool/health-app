# Direct conversation evidence — October26, 2026

The predefined Help Me Choose questionnaire was replaced by the existing voice conversation. Latest browser labels: **stop to chat / Ai assistant conversation**. Destination: **Talk to Pause**. The developer confirmed retaining voice plus existing post-exercise text feedback; no typed-chat composer was added.

- [Home with conversation icon and both direct exercise cards](01-home-390x844.png)
- [Conversation opens directly; microphone closed](02-conversation-390x844.png)
- [Isolated missing-configuration error with Home/support available](03-missing-config-390x844.png)
- [Read-only data/file preservation and actual API results](preservation.json)

All screenshots are390×844. Home, closed conversation and simulated error measured390px scroll width/844px height with no overflow. Microphone/Return Home targets56px high; Crisis Support44px, keyboard Home focus3px. No microphone/provider call on entry. Real browser verified keyboard Return Home, independent support while backend unavailable, and both direct exercise views/Exits after simulated voice failure. No contact links were operated.

The isolated browser server5189 returned voice config unconfigured and other APIs503, so its explicit microphone-button check failed before getUserMedia or a session POST; it made no real database/model request. This is mock configuration failure evidence, not a real permission/provider failure. Mock voice tests cover permission success/denial, offer/answer/session.started, Mute/End, playback, transcripts, late results and all cleanup paths. No new paid live conversation or live speech quality/adherence was tested.

Checks:86 full backend tests passed/1.460s;70 final frontend tests passed/2.737s; final35-module production build passed/12.67s. Obsolete creation tests were removed; shared context/feedback, historical reads and v4 migration coverage retained. Known non-failing Starlette HTTPX TestClient warning. No dependency installation. Existing iCloud-offloaded files delayed initial reads/startup and were hydrated; first3s local health request timed out during cold startup, later health/config200 and browser Backend ready.

Actual normal backend8000 PID54531 (saved live configuration, no mock override), existing built-output preview5173 PID38123. Retired POST /api/recommendations404 and absent from served OpenAPI; scoped GET historical conversation matched messages/content/source/status after UTC serialization normalization. All original rows exactly equal:66 sessions/11 moods/36 conversations/67 messages, including16 historical recommendations; schema7 unchanged, FK check empty. Protected report/env/voice JSON/model configuration/lifecycle/exercises/mood/crisis/session code hashes pass. No new runtime data was created by this review. Temporary failure server/tab cleaned up; normal app retained.

Changed interface owners: ConversationScreen.vue (new), HomeScreen.vue, SkillIcon.vue, VoicePanel.vue presentation, App.vue, API helper and relevant CSS. Removed RecommendationScreen.vue and recommendations.js. Backend removed the creation route/controller/store method/request input/provider recommendation methods and recommendation_policy.py; shared feedback payload helper moved intact to feedback_policy.py. Historical response projection/schema/read route remain deliberately. Removed obsolete recommendation frontend/backend test files and added test_conversation_compatibility.py; existing voice failure/text-feedback test now exercises retained post-exercise feedback. README/AGENTS/design/flow/research/contracts/verification/handoff updated.

Limitations: no typed conversation; no voice/audio/transcript saving; no new live-model/hardware/long-transcript browser test, full screen-reader/zoom/device audit pending. Existing offline retry/abrupt-close persistence and unconfirmed provider-finalization limitations remain. No report edits, paid calls, commits or pushes. Earlier recommendation evidence remains historical.

Latest copy follow-up: [Home with capitalized “Stop to chat”](04-capitalized-home.png). Production build and browser check passed.
