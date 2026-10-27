# Pause — Assignment 3.2 interactive skills

Pause is a local mental health skills **coursework prototype**, not a mental health support service. It does not diagnose, provide therapy, claim clinical effectiveness, or imply human monitoring. Testing uses fictional scenarios only.

## Current milestone and chosen direction

Paced Breathing now uses **hold to run, release to pause**. Opening is idle; the first hold or accessible Start begins one session. Four-second inhale/six-second exhale phases accumulate active time across pauses. Six cycles (60 active seconds) are the planned portion; Finish is always the explicit completion action after starting, and optional continuation never auto-ends. Exit records an exited session. Button interaction does not measure respiration. Home now opens the existing voice conversation directly through **Stop to chat — Ai assistant conversation** (the reviewed browser labels). The page is titled **Talk to Pause**. The predefined Help Me Choose questionnaire has been retired. Grounding and contextual post-exercise text feedback are preserved. No History UI or model-proposed SQL RAG is implemented. See the [hold-to-run evidence](docs/evidence/part-3-2-hold-breathing/index.md).

- Skills: paced breathing, a planned six 4-second inhale / 6-second exhale cycles (60 active seconds, optional continuation), and five sensory Grounding steps (Sight 5, Touch 4, Hearing 3, Smell 2, Taste 1), with an intended 70-second path and no forced timer.
- Journey: optional once-per-local-day mood popup → home → direct exercise or optional conversation → manually selected exercise → optional completion feedback → home. Skip, immediate Exit, and independent crisis information preserve control. Normal use requires no typing or account.
- Interface: one action at a time, light neutral colors, muted blue, large labeled controls, visible focus, generous spacing, and reduced motion.
- Personalization: minimal prior activity can label a recently used card. Stable order is the default; optional mood/activity ordering is documented as a changeable alternative, never an automatic exercise selection or restriction.
- AI: the voice assistant can discuss everyday practical next steps and optionally suggest either existing exercise; the user navigates manually. Separately, short post-exercise text responses use feedback plus optional saved mood and up to three recent supported exercise records. Code owns instructions and timing. Future SQL-based RAG remains a separate assignment capability requiring a reviewed contract before implementation.
- Tradeoffs: daily prompts still add friction, persistent safety consumes space, and minimal tracking limits personalization. The research mapping explains alternatives and reasons.

## Review documents

- [Design specification](docs/design.md): five screens, timing, AI, data, personalization, safety, and unresolved questions.
- [Research-to-design mapping](docs/research-decisions.md): R1–R4 and D1–D6, feature choices, reasons, alternatives, and limitations.
- [User flow](docs/user-flow.md): Mermaid navigation, interruptions, and optional response states.
- [Earlier Grounding-stage mockups](docs/mockups/grounding.html): static five-screen previews before Help Me Choose; current implementation evidence is in verification notes.
- [Original Part 3.1 STOP gallery](docs/mockups/index.html) and [original specification](docs/history/part-3-1-design.md): preserved design history.
- [Part 3.2 submission evidence](docs/evidence/part-3-2-final/index.md): eight required views, additional failure/loading captures, selected fictional SQLite records, and measured timing. Open this index in a Markdown viewer; screenshot links open locally.
- [Verification record](docs/verification.md): Part 3.1 evidence plus actual Part 3.2 tests/browser checks.
- [Foundation contracts](docs/design-pipeline.md): implemented responsibilities, health API, local data, and stage-specific behavior.
- [Development instructions](AGENTS.md) and [current handoff](handoffs/current.md).

Open `docs/mockups/grounding.html` directly in a local browser by double-clicking it in Finder or using Open File. Keep `styles.css` beside it. No server, network, build, or installation is needed. Buttons are inert; these previews are not a usable support route. Browser rendering, focus behavior, and viewport fit still require visual review.

## Architecture and folders

Vue/JavaScript presents views, local navigation state, and a bounded health request; exerciseTiming.js derives deterministic phases from monotonic elapsed time; sessionRecorder.js serializes background saves without blocking navigation. FastAPI/Python owns validation, controllers, configuration, SQLite access, and provider calls. Only the backend opens `data/app.sqlite3`; resolve its path relative to the project, not the current shell directory. Configuration explicitly loads `backend/.env` if it exists, without overriding process environment. `.gitignore` protects secrets/runtime data and `backend/.env.example` contains only example settings and a blank credential placeholder. No actual `.env` or key is required. Keys never appear in Vue, responses, logs, prompts, or screenshots.

```text
frontend/src/       Vue components, local check-in helper, and API client
backend/app/        FastAPI routes, health controller/model, configuration, SQLite access
data/               Ignored app.sqlite3: metadata, sessions, daily check-ins, conversations/messages
backend/data/       Earlier empty placeholder, preserved; not the runtime target
docs/               Specifications, research mapping, flow, verification, mockups
backend/tests/     API/provider/migration tests with temporary fictional databases
frontend/tests/    Node tests for timing, persistence, source labels and request state
tests/              Earlier placeholder, preserved
prompts/            Future curated instructions
handoffs/           Current state and next step
```

Existing Expedia Lite patterns are identified in the research mapping and foundation contracts. Pause source was written for this app; no travel data, UI, or provider code was copied.

## Local setup and startup

Run these commands from the repository root unless noted. Verified environment: Python 3.13.15, Node 24.20.0, npm 11.19.0. Vite requires Node `^22.18.0 || >=24.12.0`.

Backend setup (project-local packages; already installed in this workspace):

```sh
python3 -m venv backend/.venv
backend/.venv/bin/python -m pip install -r backend/requirements-dev.txt
```

Runtime requirements are FastAPI, Uvicorn, python-dotenv, and HTTPX; development tests use the same declared requirements. Do not install globally. Start FastAPI in terminal 1:

```sh
backend/.venv/bin/python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

The lifespan initializer transactionally upgrades `data/app.sqlite3` to schema version 6, adding activity and conversation/message tables if missing. It preserves previous rows; no sensitive fixtures are seeded. Actual exercise/mood/feedback actions now save records scoped to a random local application UUID. If startup cannot initialize the file, the backend fails rather than claiming readiness.

Frontend setup in terminal 2:

```sh
cd frontend
npm install
npm run dev
```

Open [Pause locally](http://127.0.0.1:5173). Vue requests `/api/health` through Vite’s proxy to port 8000, with a three-second timeout. A small status indicator reports readiness/failure; it never gates navigation. Use `127.0.0.1` consistently: `localhost` and `127.0.0.1` are separate browser-storage origins. The health indicator checks once per page load; reload after restarting the backend to refresh it.

Stop each server with Ctrl+C in its terminal. Both servers bind only to loopback. Do not deploy this coursework prototype as a mental health support service.

Verification from the root:

```sh
backend/.venv/bin/python -m unittest discover -s backend/tests -v
```

Frontend checks from `frontend/`:

```sh
npm test
npm run build
```

For an optional local production-build preview, run `npm run preview` from `frontend/` and open `http://127.0.0.1:4173`. This origin has its own daily check-in marker. The built app’s health request works through Vite preview’s proxy; production hosting/API routing is not configured by this task.

Direct health endpoint: [GET /api/health](http://127.0.0.1:8000/api/health). Expected HTTP 200 JSON: `{"status":"ok","database":"ready","model_configured":false}` when no key is configured. An unavailable database after startup returns HTTP 503 with a neutral detail. `model_configured` means only that a nonblank backend setting exists, never that a provider call succeeded. API docs are at `http://127.0.0.1:8000/docs`. Session start/end/feedback, daily-mood, POST /api/feedback-response and scoped GET /api/conversations/{id} endpoints exist. See [API contracts](docs/design-pipeline.md) for payloads, idempotency, scope, and failure responses.

### Provider configuration

No key is needed for the default `MODEL_PROVIDER=mock`. Helpful/Not Helpful show **Demo response · mock provider**. Skip submits no model request. This is a deterministic demonstration, not evidence of a live model call.

For live use, create your own ignored `backend/.env` using [backend/.env.example](backend/.env.example) as a reference; never overwrite an existing environment file. Set `MODEL_PROVIDER=live`, `MODEL_API_KEY` to a valid private key, `MODEL_NAME` to the provider's model identifier, and `MODEL_ENDPOINT` to its complete HTTPS chat-completions-compatible endpoint. The adapter sends bearer authorization and model/messages/max_tokens/temperature JSON; provider-specific APIs may need a new adapter. Do not paste keys into source, Vue, screenshots, Git, or frontend environment variables. Restart FastAPI after settings change. Process environment takes precedence over backend/.env. CORS_ORIGINS retains the exact comma-separated local-origin override.

Live mode with incomplete configuration fails explicitly; it does not silently substitute a mock. Health reports key presence only, not complete configuration or successful provider access. The provider has a finite total deadline (MODEL_TIMEOUT_SECONDS: 1–25 seconds; code default 4, verified local configuration 25), bounded HTTP response size, no redirects/tools, and no database access. Generation uses only fixed selection/feedback, an optional saved mood, and at most three recent supported exercise summaries (type, completed/exited status, optional feedback). IDs, dates/timestamps, durations, circle taps, free text and full history are excluded. Code accepts only reviewed neutral completion responses (maximum 240 characters / 40 words), or a supported structured suggestion with a matching reviewed short reason; all other output becomes an explicitly labeled static fallback. This deliberately limits conversational variety. Three controlled live requests were made during the follow-up: the first safely timed out at the original four-second limit; Not Helpful and Helpful subsequently succeeded after matching the earlier project’s reasoning setting and allowing 25 seconds. Routine tests remain mocked. Free-tier availability and latency can vary; no automatic provider retries are enabled.

The inspected Expedia Lite project at `../Assignment 1` uses **OpenRouter**, endpoint `https://openrouter.ai/api/v1/chat/completions`, model **`nvidia/nemotron-3-ultra-550b-a55b:free`**. Its root .env supplies OPENROUTER_API_KEY; OPENROUTER_MODEL is optional and absent locally, so the source default above is the effective identifier. Pause maps that credential to MODEL_API_KEY and the effective identifier to MODEL_NAME; unrelated Expedia keys/data are not copied. FastAPI uses HTTPX bearer-authenticated POST requests; python-dotenv loads configuration. No additional provider SDK or package install is needed. The API format is described in the [OpenRouter reference](https://openrouter.ai/docs/api_reference/overview).

The existing local backend/.env is now configured for live mode with owner-only permissions and excluded from Git. Do not overwrite or print it. Required settings are MODEL_PROVIDER=live, private MODEL_API_KEY, MODEL_NAME, and MODEL_ENDPOINT. Set MODEL_TIMEOUT_SECONDS=25 for the verified configuration. OpenRouter requests disable reasoning, matching Expedia Lite; other compatible endpoints receive no provider-specific reasoning parameter. The response HTTP wait in Vue is bounded at 28 seconds; ordinary activity requests remain three seconds, and Home/Crisis never wait for generation.

To switch back to deterministic testing, change only MODEL_PROVIDER=mock in backend/.env and restart FastAPI using the startup command above. To re-enable live mode, change it to live and restart. An alternative one-run mock command from the root is:

```sh
MODEL_PROVIDER=mock backend/.venv/bin/python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

Stop the existing server first to avoid a port conflict. Tests inject their own mock settings/providers and never need the real key. See [live verification](docs/verification.md) and the [live response screenshot](docs/evidence/part-3-2-live/live-response-390x844.jpg). Local services remain in live mode after this check; selecting new Helpful/Not Helpful feedback can send a real provider request.

### What this stage saves

Browser storage holds a random `pause.application-id` UUID and daily dismissal markers (`pause.checkin.dismissed.YYYY-MM-DD = dismissed`), not mood text. SQLite stores session ID/type/start/end/status (started/completed/exited), measured duration, separate entry/setup time, planned duration=60, optional feedback, and one mood/skipped value per application ID/local date with creation time. Planned duration is 70 for grounding_54321 and 60 for breathing/historical STOP. Circle selections are transient and are not saved or sent to the provider. Conversation records link session ID, exercise/feedback context, timestamp, mock/live source, and pending/succeeded/failed status. Messages have UUIDs, conversation IDs, role, ordinal, text, and timestamp. Feedback still permits one exchange per session/button; historical recommendation conversations retain their original IDs, focus/context, messages and source. New recommendation creation is removed. Existing records retain their source and content. Each conversation records its interaction kind and bounded context snapshot; failed generation retains the fixed user message and safe failure code, never an invented assistant or fallback record. There are no account records. Blocked storage uses a visit-only identity/dismissal fallback, so identity and daily guarantees cannot survive reload. Clearing browser storage creates a new identity. This local identifier is not authentication. Keep testing fictional and the runtime database out of Git.

### Navigation review

Mood choice/Skip/Close/Escape opens home. Crisis Support is inside the popup and on all main views, with U.S./territory limitations stated in its independent local resource view. Breathing opens idle, starts on the first hold or accessible Start, pauses on release/focus loss and resumes the same session. The planned six4/6-second cycles total60 active seconds; later cycles are optional continuation. Explicit Finish opens completion; Exit records exited. Textual timing, reduced motion and native Start/Pause remain available; button use does not measure respiration. Grounding shows the exact five supplied sensory instructions, 5/4/3/2/1 labeled circles, reversible noticed taps, and manual Continue/Back. Continue works at any count, including zero; no typing or descriptions. Back preserves current-exercise progress; restarting clears it. The active STOP component/card was replaced; historical stop records remain readable. Completion has optional Helpful/Not Helpful/Skip and Return Home without waiting for feedback; leaving without a choice saves skipped. Helpful/Not Helpful wait for the background session/feedback save, then request a short response with a loading notice. Return Home and Crisis Support stay enabled. Skip cancels visible response handling and requires no provider request. Leaving/Skip ignores late responses; a request already accepted by FastAPI may still finish and persist. Repeated choices reuse that session/button exchange, including failures; there is no automatic paid retry or polling. Session/mood/feedback failures are labeled not saved, and navigation never waits. Grounding has no countdown/deadline: 20+15+15+10+10=70 seconds intended, advertised as About 60–75 seconds. Actual first-instruction-to-final-Continue duration (including voluntary pauses/backtracking) and separate entry/setup are stored honestly; user pauses may exceed 90 seconds. The fictional measured run took 79.366 seconds, setup 0.001 seconds, including review/tool overhead; it is not a timed usability study. Opening crisis information ends the current exercise as exited before navigation; hiding the page pauses breathing; leaving the page attempts an exited save. An abrupt close/offline save can leave a started record; there is no durable offline outbox yet. All these paths work with the backend stopped; contact links need a compatible external connection.

See the October 19 Stage 2 entry in [verification notes](docs/verification.md) and [Stage 2 breathing screenshot](docs/evidence/part-3-2-stage-2/breathing-reduced-390x844.jpg) and [saved completion](docs/evidence/part-3-2-stage-2/completed-saved-390x844.jpg). The Part 3.1 gallery remains a static historical artifact; the new running app has separate evidence.

## Grounding revision and verification

STOP was initially selected because it was easy to implement; during review its reading-oriented interaction felt too passive. Grounding adds concrete, observable actions while keeping input tap-based and optional. This is a revised design approach for assignment development/AI-use evidence, not a clinical-effectiveness claim. R1 maps to the short intended path, R3/R4 to skip/Exit/undo/Back, D2 to one current instruction, D3 to no required disclosures, and D6 to neutral supplied copy. See the updated research/design/flow documents above.

GroundingScreen.vue and grounding.js replace the active StopScreen.vue. API identifier grounding_54321 is accepted by the existing session and feedback endpoints; fixed messages name Grounding. Schema 4 migrates the existing session/conversation CHECK constraints and planned duration in a transaction, preserving all historical STOP rows/relationships. No unrelated tables or circle-persistence fields were added. See [API/migration contracts](docs/design-pipeline.md).

Verified 35 backend tests, 23 frontend tests, production build, all five senses/counts, tap/undo, keyboard focus, optional progression, Back preservation, Exit and support from every step, saved/mock exchanges and history preservation. Paced Breathing completed unchanged in 60.015 seconds. See the Grounding entry in [verification](docs/verification.md) and [running Grounding screenshot](docs/evidence/part-3-2-grounding/sight-390x844.jpg).

The Grounding verification originally left a `MODEL_PROVIDER=mock` process override running even though backend/.env selected live. The subsequent feedback investigation removed that override and verified one new live Grounding exchange with correct source labeling and persistence. **The current backend runs in live mode.** Existing saved mock/failed exchanges remain unchanged; test a new completed session to request a new exchange rather than relabeling history.

If demo output appears unexpectedly, stop the backend, remove any inherited provider override, and restart from the project root:

```sh
env -u MODEL_PROVIDER backend/.venv/bin/python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

This lets backend/.env select the provider; it does not alter the file or print its key. Keep the explicit `MODEL_PROVIDER=mock` command only for intentional demonstrations/testing. Config is loaded at process start with process environment taking precedence; frontend reload alone cannot change the backend provider. “Model response” means an accepted saved live reply, “Demo response · mock provider” means deterministic mock, and “Static fallback · not generated by a model” means no usable generated reply was available. Live output remains limited to the exact reviewed acknowledgments; text can resemble the mock, so source/status evidence matters. See the latest investigation in [verification notes](docs/verification.md) and [Grounding live screenshot](docs/evidence/part-3-2-provider-investigation/grounding-live-390x844.jpg).

## Conversation and contextual feedback

The Home **Stop to chat** card, subtitle **Ai assistant conversation**, opens **Talk to Pause** directly. A labeled conversation icon replaces the branching-choice icon. No focus questionnaire, suggestion card, Start Suggested/Choose Other actions or recommendation loading state remains. Both exercise cards remain direct Home actions.

The existing GPT-Live voice panel starts only after Use microphone and keeps status, microphone permission handling, Mute/Unmute, End, playback recovery, temporary timed transcripts, duration cutoff and cleanup. Home/support navigation ends voice through the same lifecycle. Prompts/models/configuration are unchanged; the assistant may explain optional exercises and manual navigation, and has no automatic exercise-start tool. Pause saves no voice audio/transcripts. Existing SQLite feedback conversations and historical recommendations remain intact and readable through scoped GET `/api/conversations/{id}`.

The developer confirmed keeping the existing voice experience and post-exercise text feedback; this checkout has no general typed-chat composer. Helpful/Not Helpful still produce narrowly reviewed text feedback through the existing provider/persistence path; Skip generates nothing. No text-composer feature is added. Voice failure notices refer to other Pause features rather than removed focus choices.

POST `/api/recommendations`, its requester/controller/write helper, recommendation-only provider prompt/policy and obsolete tests were removed. The read-only historical response shape/schema and shared context/feedback infrastructure remain necessary for compatibility. No tables or saved records were deleted and schema stays7. See [conversation evidence](docs/evidence/part-3-2-conversation/index.md), [contracts](docs/design-pipeline.md) and [verification](docs/verification.md).

## Future implementation and assignment requirements

This stage implements exercises, local activity/conversation persistence, and optional narrowly constrained feedback. See the Stage 3 entry in [verification notes](docs/verification.md), [mock response](docs/evidence/part-3-2-stage-3/mock-helpful-390x844.jpg), and [missing-configuration fallback](docs/evidence/part-3-2-stage-3/missing-configuration-390x844.jpg). Retention/deletion controls and broader device/accessibility tests remain deferred.

The baseline assignment also requires SQL-based RAG: FastAPI requests a retrieval query, validates a single read-only statement with table/field and current-profile/conversation restrictions, bounds query time/results/context, then supplies relevant records and reviewed content in a second model call. The model never connects to SQLite. Writes remain separate, parameterized backend operations. Count both provider calls; use finite timeouts and reject untrusted SQL beyond a superficial SELECT check. This is a later integration plan, not an implemented feature or a required wait during exercises/ordinary history browsing. Its exact milestone and relationship to short completion feedback remain open for instructor confirmation.

Part 3.3 retains the required saved conversation-history and session table/timeline review plan. Display message IDs/order/time and session duration/completed/exited status via FastAPI, compare with SQLite after refresh/restart, and never infer clinical improvement from activity. Failed requests create no fabricated replies; failed writes cannot look saved; retries must not duplicate records. Configure and inspect services only in a later authorized implementation task. Figma/MCP capture and Vue revision are later tasks; static mockups are not editable Figma captures.

R1–R4 and D1–D6 are attributed to the instructor-provided Assignment 3 study summary; no external study citations or clinical-effectiveness claims are made. The initial crisis-information route will display U.S.-specific 988 details, explicitly limited to the United States and its territories; official resource sources and the October 15, 2026 check are recorded in the design and verification notes. Rendered mobile mockup review remains pending because the preview browser blocks local file URLs. Confirm course-specific bibliography formatting if required. The Stage 3 request supersedes the earlier documentation-only and Stage 2 boundaries. Stop for review before further features; no automatic commits or pushes. report.md is preserved.


## Hold-to-run Paced Breathing — current behavior

Open the exercise, then hold the circle to run the 4/6-second cue; release to freeze it and hold again to resume. Space/Enter work the same way. **Start without holding / Pause** is the native button alternative. Losing focus or hiding the page pauses safely. Reduced motion preserves text/countdown with a static circle. Finish opens the existing optional feedback screen, including before six cycles; Exit and Crisis Support leave as exited. No session is created before the first intentional start; pauses/resumes share its ID.

The planned duration is60 active seconds, below the90-second assignment limit. User pauses, setup, optional continuation and save latency are separate from this planned portion. The UI announces completion of the planned portion without automatically finishing. `duration_seconds` remains wall time from first start to Finish/Exit; schema7 adds nullable `active_duration_seconds`, `optional_continuation_seconds=max(0,active−60)` and `active_completed_cycles=floor(active/10)`. `planned_duration_seconds` remains60; setup is `entry_duration_seconds`. Active includes the accessibility alternative, so it is not literally time holding or a respiration measurement. Finish means user-selected completion, not proof of six cycles or correct breathing.

Schema7 preserves schema6 mode/count fields and historical values, but new sessions omit those obsolete metrics and no mode selector remains. No raw events or new AI context is stored. Failed saves remain honestly labeled; no durable retry queue is added. See [design/API contracts](docs/design-pipeline.md), [verification](docs/verification.md) and [browser/database evidence](docs/evidence/part-3-2-hold-breathing/index.md).

### Native voice conversation

Open **Stop to chat** to enter **Talk to Pause**, then select **Use microphone** when ready. No microphone permission, configuration request or provider session starts just by opening this page. Selecting the microphone checks configuration, requests audio-only permission, and connects through native WebRTC. Return Home, the independent Crisis Support route, both Home exercises and post-exercise text feedback remain available after denial/failure. Voice does not start or change an exercise. This checkout has no typed-chat composer, as confirmed for this increment.

States are Permission, Connecting, Active, Muted, Closing, Closed and Error. Active requires session.started. Mute toggles microphone tracks only; playback/session/billing continue. End stops capture immediately, sends session.close when possible, and retains remote audio/channel/peer until session.closed or a five-second deadline. Timeout/disconnect means incomplete, unconfirmed finalization. Navigation/support/unmount/page exit also stop capture; page exit cannot guarantee receipt of the final event. Duplicate Start/End and late answers remain guarded.

The full assistant's authoritative prompt configuration is [backend/app/voice_session.json](backend/app/voice_session.json): `instructions` for GPT-Live-1 and `delegation.responses.instructions` for the separate reasoning model. The personality-delivery correction adds these two fields to the earlier exact handoff; model gpt-live-1, voice gleam, delegated gpt-6-luna, reasoning and tools remain unchanged. Live is instructed to offer one concrete everyday suggestion when useful, optionally recommend either existing exercise, and ask one focused question only when needed. The backend gets its own scope/context/safety policy. Staged prompts/01 and02 and historical voice_prompts.py are references, not runtime inputs. No database context or navigation tool is supplied to voice; Crisis Support remains independent.

FastAPI snapshots this JSON at process startup. After editing it, **restart FastAPI and end/restart any existing voice session**: an open provider session keeps its original instructions. The frontend sends SDP only, never startup instructions or session.update. With `VOICE_DIAGNOSTICS=1`, the server terminal logs `voice_prompt phase=loaded` and, for a deliberately started request, `phase=outgoing`, with source filename, instruction hashes, character counts and inclusion flags. The hashes should match; raw prompts/SDP/audio/conversations/keys are not logged or returned to Vue. No paid request is needed to see the loaded fingerprint. Use normal Pause at `/` for personality testing; `/voice-diagnostic.html` deliberately retains its short no-advice transport-test prompt.

GET /api/voice/config returns only status and duration_seconds. Privately supply OPENAI_API_KEY in ignored backend/.env; it is never exposed to Vue or reused from OpenRouter. The normal voice session does not use VOICE_LIVE_MODEL; VOICE_BACKEND_MODEL is now a legacy ignored setting for this voice session: the reviewed JSON fixes gpt-6-luna. Existing text-provider configuration is unchanged. VOICE_SESSION_DURATION_SECONDS defaults to60 (1–300); VOICE_PROVIDER_TIMEOUT_SECONDS defaults to10 (0.1–25), with no retries. Restart FastAPI after server configuration/code changes. Configured status does not prove account/model access. For local diagnosis only, start FastAPI with `VOICE_DIAGNOSTICS=1` to log fixed stage/status/category values without provider text or secrets; this never creates a session by itself.

Input/output transcript deltas are displayed exactly, with start_ms/end_ms retained, ordered on the session timeline and grouped only into contiguous/overlapping same-speaker intervals, not inferred turns. Text is rendered through Vue escaping, with preserved whitespace. Transcripts exist only in component memory and clear on a fresh Start or leaving the view; no audio/transcript logging, recording or database writes are added. Provider retention defaults are not a promise of no provider retention. A transcript may contain recognition errors.

POST `/api/voice/sessions/close` accepts only `{ "session_id": "<previously issued ID>" }` (body limit1KiB). FastAPI checks its bounded,15-minute in-memory issued-ID registry before using the private key to request provider hangup. Unknown/expired IDs reject404; repeated/concurrent requests share one provider operation. The frontend uses this bounded keepalive request for late SDP results, close timeouts and page/navigation exit. An in-flight SDP fetch remains observable after End so its ID can be closed without applying its answer or reviving old UI. FastAPI also requests hangup when it detects a disconnected creation request. Only session.closed confirms finalization; a hangup acceptance returns close_requested and the UI labels finalization unconfirmed. The registry is process-local and is not production user authentication; restart, abrupt page loss, an unknown creation outcome or provider failure can prevent confirmed closure. No billing-stop guarantee or automatic retry is claimed.

Focused mocked checks from the project root: `backend/.venv/bin/python -m unittest discover -s backend/tests -p test_voice.py -v`. Tests use fictional SDP and HTTPX MockTransport; they do not require credentials or create paid sessions. Do not use a manual POST as a health check: session creation can incur charges, including initialization. [Voice API contract and source references](docs/design-pipeline.md) explain limits, errors and the current configuration. This local service is not a production authentication boundary.

Frontend mocked voice checks: `cd frontend` then `node --test tests/voice.test.js`. `npm test` includes all frontend regression checks. `npm run build -- --configLoader native` builds using the installed Node/Vite configuration loader. These tests fake MediaDevices, RTCPeerConnection, audio, timers and the FastAPI responses; they never request real microphone access or make paid calls. The browser needs HTTPS or localhost for real microphone use. Real audio/device/provider verification remains a separate authorized task.

For one deliberately started live conversation, follow the [under-60-second manual checklist](docs/verification.md#manual-live-check-not-run). The later October26 failure investigation restarted the stale backend: /api/voice/config now returns200/unconfigured instead of404. The earlier investigation found OPENAI_API_KEY missing; privately supply it in the existing ignored backend/.env, restart, and require configured status before attempting live voice. No paid call was made. The manual plan uses a45-second process-only duration override and mock text mode, preserving saved settings and preventing an extra live text call; it includes interruption, mute/unmute, End and microphone-release observations. See [actual failure evidence](docs/verification.md#actual-voice-failure-investigation) for the separate pending microphone-only diagnostic and remaining limits.


### Isolated GPT-Live diagnostic (no paid request on load)

Keep normal Pause running on ports5173/8000. Start the separate database-free diagnostic from the project root:

```sh
VOICE_LIVE_MODEL=gpt-live-1 VOICE_DIAGNOSTICS=1 backend/.venv/bin/python -m uvicorn backend.app.voice_diagnostic:app --host 127.0.0.1 --port 8001
```

Open [the isolated browser diagnostic](http://127.0.0.1:5173/voice-diagnostic.html). **Check microphone only** requests permission and immediately stops tracks without calling FastAPI or OpenAI. **Use microphone** creates a billable session: wait for explicit approval before selecting it. Nothing starts on load, and no automatic retry occurs. The diagnostic uses a short connection-test instruction, no SQLite/history/recommendations/Responses/Decisions/tools, and a30-second UI cutoff. Independent Crisis Support, End, mute and cleanup reuse existing components. The normal application's exact voice_session.json is preserved.

The diagnostic reads VOICE_LIVE_MODEL (defaults to and requires gpt-live-1), keeps OPENAI_API_KEY exclusively in FastAPI, and uses the existing finite VOICE_PROVIDER_TIMEOUT_SECONDS (default10; unchanged). Its reusable HTTP/TLS client is prepared at startup and closed on shutdown. Opt-in logs show fixed HTTP phase, timeout subtype and elapsed time, never request/response content or secrets. store:false is a session retrieval setting, not a provider-retention promise. [Diagnostic verification and remaining live-test approval](docs/verification.md#isolated-gpt-live-diagnostic--october-26-2026).
