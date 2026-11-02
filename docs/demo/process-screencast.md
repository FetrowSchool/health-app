# Pause — development process screencast

Prepared November2, 2026. **Outline and narration only; no recording exists.** Aim for roughly3–4 minutes unless the instructor specifies otherwise. Use [the common recording checklist](application-demo.md#recording-checklist-for-both-videos).

## One real failure: configured voice did not establish a session

Tell the story as evidence-driven investigation, not a claim that the original timeout's root cause was proved. Do not recreate a paid failure, alter credentials or fabricate a console log. Display the saved evidence with its actual date; a current recording of an old screenshot is historical evidence, not a replay of the original runtime event.

| Beat | What to show | Brief narration / evidence |
| --- | --- | --- |
| **1. Failure —20s** | [October26 timeout screenshot](../evidence/part-3-2-voice/05-approved-attempt-timeout.png) beside [approved-attempt.json](../evidence/part-3-2-voice/approved-attempt.json). | “The voice UI failed before a usable session started. I separated the microphone check from the provider request rather than assuming permission explained every failure.” |
| **2. Detect and localize —25s** | Only the JSON fields application_microphone_attempt and provider_attempt; do not open real network request bodies. | “The first microphone attempt was denied and sent no session POST. A separate approved native-WebRTC request used no microphone capture; it reached the provider-request stage but returned no answer before the bounded browser wait. No session ID, SDP answer or session.started was received.” |
| **3. Investigate alternatives —25s** | [minimal-diagnostic.json](../evidence/part-3-2-voice/minimal-diagnostic.json), selectively showing microphone/contract/nonbillable-network/unverified. | “A later microphone-only check succeeded and stopped its tracks without a paid request. Basic HTTPS and the nonbillable HEAD request worked, but that did not prove account access or a successful Live session. Mock tests checked our request/response handling.” |
| **4. Decision/change —20s** | [voice_provider.py](../../backend/app/voice_provider.py), `VoiceProvider.__init__`, then [voice_diagnostic.py](../../backend/app/voice_diagnostic.py), `create_diagnostic_app`. | “A confirmed gap was synchronous JSON loading inside the timed async request. The follow-up moved that snapshot into provider construction. A separate minimal diagnostic prepared its HTTP/TLS client at startup, without database, exercises or delegated reasoning. These changes improved isolation; they did not prove the old timeout's cause.” |
| **5. Verify result —25s** | [November2 live metadata](../evidence/part-3-3-clean/approved-live-outcome.json) and [sanitized transport observation](../evidence/part-3-3-clean/live-transport.txt). | “A later, separately approved single attempt succeeded: provider201 in1151ms, Active and assistant output, then automatic session.closed/microphone-off UI by39.319s. The30s active override was process-only and later removed. No retry or private transcript was retained.” |
| **6. Explain generated code —60–90s** | The breathing functions listed below, zoomed to readable size. | Use the short code explanation below; connect input → timing → saved session → tests. |
| **7. Close —10s** | [Full automated results](../evidence/part-3-3-clean/automated-results.json) and [behavior-check summary](../evaluation/behavior-checks.md). | “The fresh full run passed95 backend and85 frontend tests plus the build. Those are saved November2 results, not a rerun in this video. Connection success does not prove every spoken response is safe; remaining failures are documented.” |

### What the failure evidence does and does not establish

- **Confirmed:** permission denial prevented the initial microphone path from POSTing. The separate provider attempt had no upstream HTTP status and was categorized timeout. The browser's28s deadline expired before an answer. A prior502 was not reproduced. Do **not** narrate an observed504: that was the backend's expected timeout mapping, not a status that this browser actually received.
- **Investigated, not proved as causes:** microphone permission/device access, backend configuration/API contract, basic DNS/HTTPS connectivity and cold HTTP/TLS setup. The recorded HEAD405 is not authenticated session success. The timeout alone does not establish invalid authentication, insufficient credits, model denial, malformed SDP or a provider outage.
- **Change/decision:** the saved verification identifies synchronous full-session JSON reading inside the timed async coroutine as a confirmed implementation gap; current `VoiceProvider.__init__` snapshots it before requests. The diagnostic prepares its HTTP/TLS client at startup and adds bounded phase/subtype diagnostics. Isolate layers and retain finite deadlines/no retries, rather than weakening validation, increasing waits indefinitely or relabeling a fallback as live. None of that proves cold setup caused the original timeout. The [verification notes](../verification.md) record the original and follow-up observations; the [voice evidence index](../evidence/part-3-2-voice/index.md) links the historical materials.
- **Outcome with limits:** November2 established a new successful connection, not a retroactive explanation of October26. The three fictional semantic turns were not completed/scored, actual audibility was not independently assessed, and real manual Mute/End were not tested in that attempt. Automatic close was confirmed. Do not claim that environment edits, microphone permission or prompt changes definitively fixed the provider timeout.

The separate [prompt-delivery finding](../evidence/part-3-2-voice/prompt-delivery.json) really did find empty runtime instruction layers before a correction and verified insertion with mocks afterward. It concerns instruction delivery, not the cause of transport failure. Keep it out of this short timeout story unless explicitly labeled as a different issue. Never say “adding the prompt fixed the connection.”

## Explain one meaningful agent-assisted code section

Selected example: the current **hold-to-run/release-to-pause Breathing implementation**. The code controls an interface/timer, not actual respiration. Use this as an explanation of the reviewed agent-assisted implementation, not a claim that every line's authorship or clinical effectiveness was independently established.

### Exact files/functions to open

| Responsibility | Exact source and functions | Explain |
| --- | --- | --- |
| Input ownership | [breathingInteraction.js](../../frontend/src/breathingInteraction.js): `createBreathingControl`, returned `pointerDown`, `pointerUp`, `keyDown`, `keyUp`, `toggle`, internal `pause` | One pointer/key owns the hold. Press resumes, matching release pauses. Space/Enter repeats and duplicate pointers are ignored; native Start/Pause is an alternative. |
| Vue state/view | [BreathingScreen.vue](../../frontend/src/components/BreathingScreen.vue): `pointerDown`, `pointerEnd`, `keyDown`, `keyUp`, `toggleAlternative`, `pauseWhenHidden`, `stop`, `finish` | Wires input to control; timer `onUpdate` replaces reactive state for text/circle/progress. First `onStarted` emits the start event. Blur/hidden/page departure pauses or stops; listeners are removed on unmount. Reduced motion keeps the cue static without stopping readable timing. |
| Timing | [exerciseTiming.js](../../frontend/src/exerciseTiming.js): `breathingState`, `createBreathingTimer`, internal `snapshot`, `pause`, `clearFrame`, `tick`, returned `resume`, `stop`, `summary` | Uses injected monotonic `performance.now()` from the component, accumulated active time and requestAnimationFrame. Six planned cycles are60s; optional continuation is allowed. Generation tokens invalidate stale callbacks. |
| Navigation/session ownership | [App.vue](../../frontend/src/App.vue): `choose`, `instructionStarted`, `endExercise`, `complete`, `goHome`, `openSupport` | `choose` allocates one UUID; database start waits for the first intentional timer start. Finish records completed; Exit/support records exited. Stop is idempotent. Navigation does not wait for persistence. |
| Save sequencing | [sessionRecorder.js](../../frontend/src/sessionRecorder.js): `createSessionRecorder`, `ensureStarted`, `ensureEnded`, `enqueue`, returned `start`, `finish`, `feedback`, `settled` | Queues start/end/feedback for that one session, freezes the first terminal payload and reports unsaved writes honestly. Guards prevent duplicate work and stale acknowledgments from hiding a newer save. No durable offline outbox. |
| HTTP and database boundary | [api.js](../../frontend/src/api.js): `createActivityAPI` → `startSession`/`endSession`; [activity_controller.py](../../backend/app/activity_controller.py): `start_session`, `end_session`, `transaction` | Vue POSTs `/api/sessions`, then PATCHes `/api/sessions/{id}` with validated summaries. FastAPI alone makes scoped, parameterized SQLite writes. Raw hold/key events are not saved; the model cannot control timing. |

### Short narration, with a worked example

“The circle is a real control. On press, `pointerDown` calls the timer's `resume`; matching release calls `pause`. The component publishes the timer snapshot into Vue's reactive state, which updates the cue and instruction.

“Active milliseconds are accumulated time plus the current running interval. `breathingState` takes active time modulo10,000: the first4,000 milliseconds are inhale and the next6,000 are exhale. `performance.now()` measures elapsed time, so delayed animation frames do not lengthen a phase by counting frames.

“For example, hold2.3 seconds, pause10 seconds, then hold2.1 seconds. Active time is4.4 seconds—already in exhale—while wall time is14.4 seconds. Pausing adds the current interval once, cancels the scheduled frame and invalidates old callbacks. Resume starts another interval without resetting the accumulated time.

“One chosen session ID is saved on the first start. Finish or Exit submits the final status, wall duration and active summary through FastAPI. Completed cycles are `floor(activeSeconds/10)`; optional time is `max(0, activeSeconds−60)`. A completed status means the person chose Finish, not proof of six cycles or correct breathing. Failed writes stay labeled unsaved and never block Exit.”

### Tests and recorded evidence to point to

- [breathingInteraction.test.js](../../frontend/tests/breathingInteraction.test.js): `opening is idle; primary hold starts once and release/resume preserves active progress` uses exactly the2.3s/10s/2.1s example; confirms one start,4.4s active and14.4s wall.
- Same file: `Space/Enter and accessible Start/Pause work without repeats or duplicate starts`, `planned completion is a notice, optional cycles continue, explicit stop is terminal`, and `first interaction, multiple pauses, early Finish and feedback create only one saved session`.
- [exercises.test.js](../../frontend/tests/exercises.test.js): `4-second inhale / 6-second exhale pattern continues beyond the six planned cycles`, delayed-frame/stale-callback test, in-flight Exit test and honest save-failure test.
- [test_breathing_hold.py](../../backend/tests/test_breathing_hold.py): saved active summaries, early Finish/Exit and preservation checks; [full result IDs](../evidence/part-3-3-clean/automated-results.json) distinguish actual passing tests from a proposed test plan.
- [Clean browser/database evidence](../evidence/part-3-3-clean/database-evidence.json): actual recorded run72.036 active seconds including12.036 optional continuation, setup7.208s separately; [six-cycle capture](../evidence/part-3-3-clean/04-six-cycles-complete.png). The notice was first sampled at65s; don't present that as proof the notice first appeared at exactly60.000s. Deterministic tests check the60,000ms boundary.

If you run tests while filming, show their real new output and label mocked providers. Otherwise explicitly call the files saved verification evidence. No new test run, live model call or recording was performed by preparing this outline.

## End-of-take checks

Use the [shared checklist](application-demo.md#recording-checklist-for-both-videos): save the actual process video, review playback/captions and private content, then create/test the real viewer link. Current status: **process screencast not recorded and no viewing link supplied**. Do not invent a recording, result, root cause or share URL to fill that gap.
