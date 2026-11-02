# Part 3.3 evaluation evidence — November 1, 2026

Read the [evaluation matrix](../../part-3-evaluation.md) first. It records26 scenarios:23 executed (22 passed,1 failed),3 live cases not run. BC1 passes tested routes; BC2 is partial pending live refusal behavior; BC3 fails the unsupported spoken-suggestion criterion while fixed exercise logic passes. This is not a blanket submission-readiness claim.

## Fresh automated and database evidence

- [Backend results](backend-results.json):92/92, temporary fictional SQLite and mocked providers; exact test IDs/outcomes.
- [Frontend results](frontend-results.json) and [TAP](frontend.tap):83/83, controlled clocks and fake browser/API objects. Four added voice tests exercise ordinary/exercise/refusal transcript transport and the unsupported-content boundary. S19's test passes by observing a failed product criterion.
- [Production build](production-build.txt):37 modules, completed successfully. Evaluation entry excluded from production inputs.
- [Browser observations](browser-observations.json): executed UI checks with explicit simulated-voice provenance.
- [Fictional database/API evidence](database-evidence.json):1 skipped mood,5 sessions (4 exited/1 completed Grounding),1 mock-feedback conversation,2 saved messages. Exact rows and History JSON survive actual test-backend process restart; FK check empty. SQLite/API/UI IDs, order, content and completed parent session match. Equivalent UTC timestamp formats (+00:00/Z) are explicitly normalized for message comparison. Five simulated session POSTs; zero real provider calls.
- [DOM record IDs](browser-record-ids.json): actual visible fictional History/message data attributes and text, not private application identity.
- [Preservation](preservation.json): original runtime rows/schema and protected production source/report/env hashes. No private row values or credential hashes exported.
- [Read-only inspection SQL](inspection.sql): for the isolated fixture database only.

## Browser captures — all MOCK previews

Actual Vue app views at390×844, with a test-only banner adding36px. Fake microphone/WebRTC and voice API; deterministic text feedback. No actual remote audio, real microphone or model response. Production success UI says “Live model” in06 because the harness supplies that contract; the visible simulated banner and this index identify it as mock. These images must never be submitted as live-model proof. Vertically scrollable History/support/transcripts are expected; this is not a complete accessibility or production layout audit.

| Capture | Observed state |
| --- | --- |
| [01 daily mood](01-daily-mood-mock.png) | First-day dialog, Skip/close/support |
| [02 breathing idle](02-breathing-idle-mock.png) | Ready before interaction |
| [03 breathing paused](03-breathing-paused-mock.png) | Hold starts; release pauses |
| [04 Grounding](04-grounding-mock.png) | Hearing3, optional counters and Continue |
| [05 completion/feedback](05-completion-feedback-mock.png) | Truthful Demo/mock-provider feedback |
| [06 scripted voice](06-active-scripted-voice-mock.png) | Canned ordinary/suggestion/refusal deltas, simulated Active |
| [07 voice failure](07-provider-failure-mock.png) | Mock503 with Home/support |
| [08 History](08-history-mock.png) | Completed/exited, active/total durations, feedback |
| [09 saved messages](09-saved-conversation-mock.png) | Actual fictional saved user/assistant order |
| [10 support](10-crisis-mock.png) | Independent local route; contact links not used |
| [11 backend offline](11-backend-offline-history-mock.png) | History error; navigation remains; footer stale startup status |

## Repeatable commands

From the project root with existing dependencies; no install or paid call:

```sh
backend/.venv/bin/python -m backend.tests.evaluation_run docs/evidence/part-3-3-evaluation/backend-results.json
cd frontend
node --test --test-reporter=tap tests/*.test.js
npm run build
```

The first command is the existing unittest suite with a small outcome-JSON runner. The frontend JSON was derived from the saved TAP `ok` records and totals; it is not a second test run. The only initial harness-build error was a missing closing brace in the test entry, corrected before the successful build/browser run. Later restart/import waits and a5-second local read timeout were resolved by restoring existing iCloud-offloaded files; no provider timeout or package installation occurred in this evaluation.

Optional isolated browser reproduction, in separate terminals from the repository root:

```sh
# Select a new temporary directory; retain it if comparing records after restart.
PAUSE_EVAL_DIR=$(mktemp -d /private/tmp/pause-evaluation-XXXXXX)
export PAUSE_EVAL_DIR
node frontend/tests/evaluation-browser/build.mjs "$PAUSE_EVAL_DIR/browser-dist"
PAUSE_EVAL_DIR="$PAUSE_EVAL_DIR" backend/.venv/bin/python -m uvicorn backend.tests.evaluation_server:app --host 127.0.0.1 --port 8190
```

```sh
# Set this to the exact directory printed/selected in the first terminal.
node frontend/tests/evaluation-browser/serve.mjs /absolute/temporary/directory/browser-dist
```

Open localhost5290 in a fresh test browser profile/origin state at390×844. Follow S01–S10, S14–S17, S20/S22 from the matrix. Touch `voice_failure` inside that temporary directory for one mock voice503, then remove that flag to restore simulated success. A `feedback_failure` flag similarly selects a deterministic text-provider failure. These flags affect only the evaluation server. Do not change normal backend/.env or seed the real database. The fake peer emits all scripted transcript events after session.started; it simulates overlap, not real audible interruption. No real microphone permission should appear.

For restart comparison: read all rows/history before shutdown, stop only8190, confirm History failure/support, restart the same command/directory, compare every row and scoped GET again. Read-only connections use `file:/absolute/temporary/directory/evaluation.sqlite3?mode=ro`. Compare one conversation's IDs/messages/parent session to DOM data attributes; omit app_id from exports. The executed preview used a temporary equivalent of the checked-in serve helper; the helper has an additional static-preview smoke check.

Stop only the test processes8190/5290, close the test tab and reset viewport when done. Normal review services8000/5173 and the separate8001 diagnostic remain independent. Do not select the normal app microphone during routine evaluation. Live steps and approval boundary are in the [evaluation](../../part-3-evaluation.md).
