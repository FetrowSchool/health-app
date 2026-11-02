# Clean setup and full verification — November 2, 2026

Branch `part-2`, base `48f912d1936142e230ae427f8592c616a6b7c6bf`. No commit/push or report.md edit. Original production source, credentials and database preserved. Installs occurred only in the temporary verification checkout.

## Checkout provenance and setup

[Snapshot evidence](snapshot.json): local `git clone --no-hardlinks --no-checkout`, checkout part-2, then overlay236 current non-ignored working files. This is a fresh dependency/runtime setup of the **current working-tree snapshot**, not proof that uncommitted features are in a pristine Git checkout. Plain HEAD lacks HistoryScreen.vue, routes/history.py and the new evaluation documents. Publication/reproducibility from Git alone remains incomplete until an explicitly requested commit includes them; none was made.

No backend/.env, SQLite, .venv, node_modules or dist was copied. No inherited app credentials/provider overrides were present. The clean app used default mock settings. The private test directory is `/private/tmp/pause-clean-j9rfmi3h/checkout`; keep its fictional database separate from the original.

Executed README commands in that copy:

```sh
python3 -m venv backend/.venv
backend/.venv/bin/python -m pip install -r backend/requirements-dev.txt
# From frontend/:
npm install
# From the root, terminal1:
backend/.venv/bin/python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
# From frontend/, terminal2:
npm run dev
# After the build, another frontend/ terminal:
npm run preview
```

Both dependency installs exited0. [Pip install](pip-install.txt), [npm install](npm-install.txt), [installed versions](dependency-versions.json). Python3.13.15, Node24.20.0, npm11.19.0; FastAPI0.162.0/Uvicorn0.54.0/HTTPX0.28.1/Pydantic2.14.2; Vue3.5.44/Vite8.3.4/plugin-vue6.0.10. npm audited37 packages with0 vulnerabilities at install time; optional fsevents install-script approval warning did not block dev/build. No extra scripts were approved. Versions are observed, not newly pinned.

`pip check` reported no broken requirements. The existing package-lock remained byte-identical after npm install; no dependency file was copied back to the original.

The README's stale schema6 description was corrected to7 before clean startup. Fresh-checkout/no-env/inherited-settings and occupied-port instructions were clarified; affected startup/database/proxy steps were then executed. The original idle8000/5173 servers were temporarily stopped so these exact port commands could not connect to the original backend. [Startup](startup.json) proves backend8000, Vue dev5173 and production preview4173 all reported the same ready database/model_configured:false and unconfigured voice. SQLite initialized schema7 with zero activity rows; only metadata existed. Original services were restored afterward.

## Full automated results

- [Backend output](backend-tests.txt): **95 passed**,1.662s. All provider transports mocked; temporary fictional databases.
- [Frontend output](frontend-tests.txt): **85 passed**,0failed/0skipped,118.411042ms. Media/voice/model mocks. This is Node's default text reporter, not TAP despite the original temporary filename.
- [Build](production-build.txt): **37 modules**, success282ms.
- [Machine-readable results](automated-results.json):180 distinct tests, exact test IDs; subset/subcase runs not counted again. Existing boundary tests intentionally pass while documenting failed voice-content rejection.

## Fresh real-browser evidence

Actual production app at390×844 from the clean build on4173, real FastAPI/default MockProvider and new SQLite. No fake MediaDevices/WebRTC/voice endpoints in this browser run. No API credentials. Separate later approved live attempt is identified below.

| Capture | Result |
| --- | --- |
| [01 daily mood](01-daily-mood.png) | Fresh dialog; Tab reaches labeled Calm button; Escape skips and saves skipped. |
| [02 Home keyboard](02-home-keyboard.png) |390×844/scrollWidth390/height844; visible3px focus; direct cards96px, support44px, History52px. |
| [03 reduced-motion Breathing](03-breathing-reduced-motion.png) | Accessible Start without holding; cue stays static, countdown advances; polite phase announcement attribute. |
| [04 planned cycles](04-six-cycles-complete.png) | First sampled planned-complete notice at Active1:05; optional continuation, no forced exit. |
| [05 mock feedback](05-mock-feedback.png) | Helpful saved; Demo response · mock provider, actual deterministic reply. |
| [06 Grounding](06-grounding-keyboard.png) | Keyboard counter/Back preservation, exact five senses and optional Continue. |
| [07 voice unconfigured](07-voice-unconfigured.png) | Explicit failure before microphone permission/session creation; other features remain. |
| [08 History](08-history.png) | Four sessions:2 completed/2 exited; durations/feedback and one mock conversation. |
| [09 saved messages](09-saved-messages.png) | Actual user→assistant records/source, chronological. |
| [10 offline support](10-support-backend-offline.png) | After actual clean FastAPI shutdown, History fails honestly and local support opens. Contact links not used. |

[Browser observations](browser-checks.json) and [DOM record IDs](browser-records.json). Keyboard verified Tab/Enter exercise selection and counter toggle, Escape modal dismissal, focus transfer,3px outlines and labels/pressed states in the accessibility tree. Reduced motion rendered transform:none at multiple real timer observations. Selected actual foreground/background ratios: heading11.82:1, prototype5.47:1, exercise card12.48:1, support7.33:1. This is not a complete contrast/screen-reader audit.

At320px Home reflowed without horizontal overflow (scrollWidth320, height846); vertical scrolling retained controls. Native Cmd-plus had no measurable viewport/DPR effect in the in-app browser; reset Cmd0. **Actual200% browser zoom unverified.** Accessibility-tree semantics/polite live-region attributes were inspected, but actual VoiceOver speech/order, announcements and broader assistive technology/device tests were not run.

## Database and timing

[Database evidence](database-evidence.json): read-only sqlite3, integrity_check=ok/FK empty;1 skipped mood,4 sessions,1 mock conversation,2 ordered messages. Scoped HTTP GETs and actual DOM match IDs/order/content/parent session, with equivalent +00:00/Z UTC normalization. No original database values copied. [Browser IDs](browser-records.json) contain fictional records only.

Real clean backend PID86553 stopped/restarted PID87546; every row and History response remained identical. Browser reloaded the same History after restart. No duplicates or voice audio/transcript records.

Breathing planned sequence remains6×(4+6)=60 active seconds, confirmed by fresh deterministic tests. The real run first sampled completion at65 active seconds and finished at72.036 active/72.038 wall, including12.036 optional continuation; setup7.208s separately. It was not automatically stopped at60, and no claim of measuring exact real-time notice onset or respiration is made. Grounding manual fictional walkthrough29.313s/setup0.001; this fast optional-counter traversal verifies behavior, not a representative70-second sensory practice or clinical benefit. Brief exits persisted exited. User pauses/continuation can extend elapsed time.

## Live-model evidence: historical versus new

Historical OpenRouter successes are supported by [October19 final evidence](../part-3-2-final/index.md), selected saved live conversations and screenshots for the retired questionnaire/feedback, requested model `nvidia/nemotron-3-ultra-550b-a55b:free`. They were reviewed, not repeated. [Earlier voice attempt](../part-3-2-voice/approved-attempt.json) timed out; [prompt delivery](../part-3-2-voice/prompt-delivery.json) verified only mocked prompt insertion. Before this stage, those files did not establish GPT-Live success.

The user explicitly approved **one** short paid attempt during this verification. It ran in the **original app**, with the existing server-side key, no copied credential or saved-env edit, process-only active duration30s and no retry. [Approved live result](approved-live-outcome.json), [sanitized transport observation](live-transport.txt).

Observed: exactly1 POST /api/voice/sessions; provider/application HTTP201, provider request1151ms; browser reached Active, received actual assistant output, then automatically closed. At39.319s after the microphone click, UI reported session.closed and microphone off; Home/support worked afterward. The audio element was unpaused/readyState4; actual audibility was not independently scored. No transcript content/audio exported or persisted. The live screenshot was excluded because it captured incidental non-script speech; no private transcript image is included. Normal60-second configuration restored. Provider final usage/billing amount was not inspected.

The fictional three-turn script was **not completed**, so ordinary-conversation quality, exercise recommendation, refusal/interruption remain NOT SCORED. Actual Mute/Unmute/manual End were not exercised in this attempt; automatic duration End/confirmed closure was observed. Mock coverage remains distinct. No second attempt was made or is authorized by this approval.

Live variation matters for: an ordinary fictional schoolwork request, an optional existing-exercise recommendation, and interruption/change of direction/refusal. These remain the small proposed semantic-evaluation selection; another paid session needs new approval. Do not infer universal safety from transport success. BC3's unsupported-exercise/therapy transcript failures remain unresolved.

Current [official WebRTC guidance](https://developers.openai.com/api/docs/guides/voice-webrtc) and [session lifecycle guidance](https://developers.openai.com/api/docs/guides/live-conversations) were fetched for the approved attempt: successful HTTP alone is not Active, and finalization is confirmed by session.closed. These references support the interpretation, not a claim that all live scenarios passed.

## Readiness and preservation

**Ready for a supervised local demonstration of exercises, mock feedback, saved History, personalization, offline support and a now-observed live voice connection. Not a complete published-checkout or all-safety/accessibility sign-off.** Outstanding: uncommitted History/evaluation files absent from HEAD, scripted live semantics, voice content-boundary failures, physical-device/screen-reader/zoom coverage, no durable offline retry queue, abrupt-close started sessions, local UUID is not authentication,20-row History/no pagination, no retention UI. Fixed-query History is not the separately specified model-proposed SQL RAG.

[Preservation](preservation.json) records original source/report/env and SQLite comparison without private values. Temporary clean services stopped; test tabs12/13 closed/viewport reset. Original8000/5173 and independent8001 retained/restored with no mock or duration override. Private clean checkout retained for review. No commit, push or report.md edit.

[Restored-service checks](restored-services.json): original backend88692/frontend87670; model_configured:true, voice configured/duration60, diagnostic30937 unchanged.56 protected source/report/env hashes and all73 sessions/15 moods/36 conversations/67 messages preserved exactly, schema unchanged/FK empty. No voice records added. Existing iCloud-offloaded files delayed original-service restart; materialized existing files, no original installs or configuration changes.
