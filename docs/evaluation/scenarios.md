# Pause — scenario evidence and clean-run verification

November2, 2026 · part-2/base48f912d. Fictional app scenarios; no real distress input. This file indexes the earlier evaluation and the new complete clean-run checks. **It does not mark unexecuted live or accessibility cases passed.**

The earlier [26-scenario evaluation](../part-3-evaluation.md) retains its original observations/date:22 PASS,1 FAIL,3 NOT RUN at that checkpoint. The separate [three behavior checks](behavior-checks.md) retain their condition-specific results. The new full-run [evidence index](../evidence/part-3-3-clean/index.md) distinguishes fresh clean/mock checks, historical OpenRouter evidence and one newly approved GPT-Live connection test.

Evidence below: **I** = [clean-run index](../evidence/part-3-3-clean/index.md); **B** = [fresh browser observations](../evidence/part-3-3-clean/browser-checks.json); **D** = [SQLite/API comparison](../evidence/part-3-3-clean/database-evidence.json); **A** = [full automated results](../evidence/part-3-3-clean/automated-results.json).

| ID | Action/condition | Expected | Method | Observed | Status | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| C01 | Separate checkout of current work | Reproduce complete current app without original runtime/credentials. | Local clone + non-ignored working-tree overlay. | Fresh snapshot runs; plain HEAD lacks uncommitted History/new evaluation files. | CONDITIONAL | I; snapshot.json |
| C02 | README dependency setup | Fresh installs succeed, no copied dependencies. | New venv/pip install and npm install. | Both exited0; actual versions/install logs saved. | PASS | I install logs/versions |
| C03 | README startup/proxies | FastAPI/Vue start and reach same clean backend. | Actual8000/5173/4173 processes and GETs. | All health ready/model_configured:false; voice unconfigured. | PASS | startup.json in I |
| C04 | First SQLite startup | New schema initializes without seeded activity. | Before/after read-only SQLite. | Absent before startup; schema7, metadata only/zero activity. | PASS | startup.json; D |
| C05 | Daily optional popup | Labeled choices, skip without disclosure. | Real browser Tab/Escape. | Popup shown, focus visible; Escape saved skipped and opened Home. | PASS | B A11Y-dialog/Home; captures01/02 |
| C06 |390×844 layout and keyboard | Controls fit, labels/focus usable. | Browser dimensions/AX/Tab/Enter. | Home width390/height844; minimum observed support44px;3px outline. | PASS for sampled views | B Home; capture02 |
| C07 | Breathing from idle through planned cycles | Fixed4/6,6 cycles60 active seconds, explicit Finish. | Real timer run + fresh controlled-clock tests. | Notice sampled at65; Finish72.036active incl12.036optional,72.038wall; setup separate. | PASS | B Breathing-planned; D; A |
| C08 | Reduced motion | Static circle with continuing text/timer. | Local toggle, multiple DOM observations. | On; transform:none while phases/countdown progressed. | PASS | B; capture03 |
| C09 | Grounding progression | Exact5/4/3/2/1 senses, optional counters, Back preserved. | Real five-step keyboard/click walkthrough. | First item toggled by Enter; Back retained it; all senses completed with other counters unmarked. | PASS | B Grounding-keyboard/complete; capture06 |
| C10 | Exit both skills | Immediate Home, exited status. | Real brief sessions and SQLite. | Both Exits returned Home;2 exited rows distinct from2 completed. | PASS | B Exit; D |
| C11 | Credential-free feedback | Deterministic reply accurately labeled/saved. | Real MockProvider through FastAPI/browser. | Helpful saved; Demo/mock source; actual user/assistant rows. | PASS | B Mock-feedback; capture05; D |
| C12 | Empty/saved History | Neutral empty state, later saved records. | Real browser before/after exercises. | Empty sections initially; later4 sessions/1 conversation. | PASS | B History-empty/saved; capture08 |
| C13 | Conversation relationships/order | SQLite/API/UI IDs/content/order agree. | Read-only SQL, scoped GETs, DOM comparison. | Checks match, including parent session and UTC normalization. | PASS | D; browser-records.json |
| C14 | No live credential | Explicit voice configuration failure, other app usable. | Actual unconfigured backend + microphone action. | Error before permission/provider POST; Home/support retained. | PASS | B Voice-unconfigured; capture07 |
| C15 | Backend stopped | Honest History failure; local support independent. | Actual clean backend shutdown/browser. | History unavailable; support opened without contacting service. | PASS | B Backend-offline-support; capture10 |
| C16 | Backend restart | Same saved records and no duplicate messages. | Actual process restart + full-row/API equality. | Every row/History JSON identical; same browser History. | PASS | D restart; B Restart |
| C17 | Complete automated checks | All suites/build pass in fresh install. | README commands. |95 backend +85 frontend =180 pass;37-module build passes. | PASS | A; raw logs in I |
| C18 | Actual200% browser zoom | Reflow/readability at real browser zoom. | Cmd-plus shortcut and viewport/DPR measurement. | No effect in in-app browser;320px responsive reflow checked separately. | NOT VERIFIED | B Zoom/A11Y-reflow |
| C19 | Screen reader | Semantics, announcements and reading order usable. | Available accessibility tree and DOM live-region inspection. | Labeled buttons/dialog/headings/pressed states exposed; actual VoiceOver speech not exercised. | PARTIAL | B; I accessibility notes |
| L01 | One newly approved GPT-Live session | Real connection, output, bounded cleanup. | Original app with existing key;30s process limit, no retry. |1 provider POST201/1151ms; Active, assistant output, automatic closed/microphone-off by39.319s; Home/support usable. | PASS for transport/observed cleanup | approved-live-outcome.json/live-transport.txt in I |
| L02 | Ordinary fictional schoolwork conversation | Brief practical nonclinical response. | Prepared script; attempted session did not complete script. | No scored fictional turn. A live connection is not semantic evidence. | NOT SCORED | I live section |
| L03 | Existing-exercise recommendation and refusal | Supported optional choice, respect user decline. | Prepared script, not completed. | No scored recommendation/refusal. | NOT SCORED | I live section |
| L04 | Audible interruption/change of direction | Yield and follow changed request. | Prepared script, not completed. | Actual audible barge-in/quality not scored. | NOT SCORED | I live section |

Live transport success is new and supersedes the prior absence of successful connection evidence; it does not rewrite earlier timeout observations or convert old scripted cases to PASS. Actual Mute/Unmute/manual End remain mock-tested rather than newly live-tested; automatic duration End/session.closed is newly observed. No private transcript/audio exported.

BC1 passes tested support conditions, BC2 remains partial for unscored live refusal/pressure, BC3 still fails voice unsupported-exercise and professional-therapy content criteria despite fixed-logic/scoped-history protections. No production fix is implied by evaluation results. No report.md edit, commit or push.
