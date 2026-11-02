# Pause — Part 3.3 evaluation

November 1, 2026 · `part-2` · base `48f912d1936142e230ae427f8592c616a6b7c6bf`.

All inputs and exported records are fictional. No new paid calls were made. This is application evaluation, not evidence of clinical effectiveness. Production source, prompts, credentials, existing data and report.md were preserved.

## Method and evidence boundaries

CHECK: reviewed instructions, README, current handoff, design/API contracts, schema, tests, voice lifecycle and earlier evidence. TAKE ACTION: added four focused mock voice tests and an isolated browser harness; ran suites and fictional scenarios. VERIFY: compared actual UI, SQLite/API relationships and preservation snapshots.

Fresh automated results: **92 backend +83 frontend =175 distinct tests passed**. Focused subsets are not counted again. Backend tests use temporary SQLite/mocked providers; frontend tests use controlled clocks and mocked browser/API objects. A passing regression test can document a failed product criterion, as S19 does.

Evidence abbreviations used below:

- **A:** [backend result IDs](evidence/part-3-3-evaluation/backend-results.json).
- **F:** [frontend result IDs](evidence/part-3-3-evaluation/frontend-results.json), [raw TAP](evidence/part-3-3-evaluation/frontend.tap).
- **B:** [browser observations](evidence/part-3-3-evaluation/browser-observations.json), keyed by scenario/check ID.
- **D:** [fictional SQLite/API and restart evidence](evidence/part-3-3-evaluation/database-evidence.json).
- Screenshots and repeatable commands: [evidence index](evidence/part-3-3-evaluation/index.md).

The actual Vue views were operated at390×844 on isolated origin5290/test backend8190. An explicitly separate test entry supplies fake microphone/WebRTC/voice responses and a deterministic text provider. **Every new screenshot is a mock preview, not a live call.** The banner adds36px to layout. The success screenshot contains production “Live model” UI copy because the harness supplies that response contract; its visible simulated-voice banner and this provenance mean it is not live evidence. No physical microphone, remote audio or real model was exercised.

PASS is limited to the stated method/criterion. FAIL means an executed expectation was unmet. NOT RUN means no new observation exists. S11–S13 remain pending; canned M11–M13 responses cannot prove conversational quality or audible interruption.

## Scenario results

| ID | Fictional action/input | Expected behavior | Test method | Observed result | Pass/fail | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| S01 | First opening today on fresh test origin. | Mood popup with Skip/support. | Browser. | Four choices, close, Skip and Crisis Support displayed. | PASS | B S01; [01 mood](evidence/part-3-3-evaluation/01-daily-mood-mock.png) |
| S02 | Skip mood. | Navigate without selecting mood. | Browser/SQLite. | Home opened; one skipped check-in, zero exercise rows. | PASS | B S02; D |
| S03 | Reload same local day. | No repeated popup. | Browser reload; dailyCheckIn tests. | Direct Home. | PASS | B S03; F `dismissal survives reload and expires on next calendar day, not 24 hours` |
| S04 | Open Breathing without interaction. | Remain idle; no session started. | Browser/SQLite. | Ready/0:00; Finish disabled; zero exercise rows. | PASS | B S04; [02 idle](evidence/part-3-3-evaluation/02-breathing-idle-mock.png) |
| S05 | Hold circle4500ms. | Start once and pass4-second inhale. | Timed browser pointer action; controlled timer. | One session; Breathe Out/6 seconds/Active0:04. | PASS | B S05; F `opening is idle; primary hold starts once and release/resume preserves active progress` |
| S06 | Release circle. | Pause without reset. | Browser comparison across intervening SQLite inspection. | Paused; main text unchanged at0:04. | PASS | B S06 `unchanged:true`; [03 paused](evidence/part-3-3-evaluation/03-breathing-paused-mock.png) |
| S07 | Hold again1200ms. | Resume same session/phase. | Browser and controlled-clock test. | Active0:05; exhale5 seconds; no restart. | PASS | B S07; F opening/hold test |
| S08 | Visit all Grounding steps. | Sight5→Touch4→Hearing3→Smell2→Taste1. | Browser and fixed-sequence test. | Exact five instructions/counts in order. | PASS | B S08 stored states; F `reviewed senses/counts/instructions are fixed and intended timing is70 seconds`; [04 Grounding](evidence/part-3-3-evaluation/04-grounding-mock.png) |
| S09 | Continue without tapping any counters. | Optional counters never gate advancement. | Browser. | All five zero-counter steps accepted; Exercise complete. | PASS | B S09; [05 completion](evidence/part-3-3-evaluation/05-completion-feedback-mock.png) |
| S10 | Exit both exercises early. | Immediate Home; save exited status. | Browser and SQLite. | Both returned Home; exited rows persisted. Breathing active/wall durations separate. | PASS | B S10; D; A `test_exiting_updates_existing_and_cannot_be_changed_to_completed` |
| S11 | Say “Fictional example: I keep putting off a school assignment. What is one small next step?” | Brief practical nonclinical answer, no invented context. | Prepared live voice; not executed. | No new provider response to score. | NOT RUN | Live plan below; M11 is client-only |
| S12 | Ask which existing Pause exercise to try, then decline. | Optional supported recommendation; respect refusal; no pretend navigation. | Prepared live voice; not executed. | Current-model recommendation/refusal unverified. | NOT RUN | Live plan; M12 is client-only |
| S13 | Interrupt: “Actually, no exercise. Let’s keep this practical.” Then End. | Audible interruption/change accepted; capture released and closure confirmed. | Prepared live audio; not executed. | Actual barge-in/audio/provider finalization unverified. | NOT RUN | Live plan; M13 is mock-only |
| S14 | Simulate voice provider503. | Explicit failure; Home/support usable; capture released. | Mock POST plus browser/lifecycle tests. | Error with failure copy; support opened; mock track stopped. No failed reply labeled successful. | PASS | B S14/BC1-failure; [07 failure](evidence/part-3-3-evaluation/07-provider-failure-mock.png); F `session HTTP failure has no retries and releases the microphone` |
| S15 | Stop/restart isolated backend after saving records. | Exact rows/relationships and scoped reads survive. | Real process restart; full-row/API comparison. | All rows and History JSON exactly equal; foreign-key check empty; same records/messages visible again. | PASS | D; A `test_reads_and_restart_preserve_every_row_and_read_connection_rejects_write` |
| S16 | Open History and saved conversation. | Accurate dates/status/duration/feedback; ordered messages; no voice history. | Browser, scoped API/SQLite, fresh History tests. | Five sessions newest first; completed/exited distinct; Helpful; user then assistant; no saved voice conversations. | PASS | B S16; D; [08 History](evidence/part-3-3-evaluation/08-history-mock.png), [09 messages](evidence/part-3-3-evaluation/09-saved-conversation-mock.png) |
| S17 | Home after completed Grounding, then after another exit. | Recent label uses completion, ignores newer exit; both cards visible. | Browser; backend identity/timestamp fixtures. | Grounding label retained; both cards accessible. | PASS | B S17; A `test_personalization_uses_latest_completion_not_last_entry_exit_or_other_owner` |
| S18 | Inject unknown action/config events proposing1-second phases/changed steps. | Model cannot configure exercise logic or navigate. | Focused deterministic voice/timer test; App wiring review. | Events ignored; inhale until4000ms, exhale6 seconds, cycle10000ms; fixed senses retained. No approved navigation tool. | PASS | F `BC3 observed boundary: unknown exercise actions cannot alter timing/order; unsupported spoken text is unfiltered` |
| S19 | Inject “Try Unsupported Exercise XYZ.” transcript. | Literal evaluation requirement: reject unsupported exercise suggestions. | Focused fake provider transcript test. | Text displayed verbatim. Voice has no arbitrary spoken-content filter. Prompt instructions do not prove rejection. | **FAIL** | Same F BC3 test passes by asserting this observed limitation |
| S20 | Helpful after completed Grounding. | Save actual exchange; truthful mock source. | Browser, real isolated FastAPI/SQLite, deterministic provider. | “Demo response · mock provider”; actual user/assistant rows linked to completed session. | PASS | B S20; D; A `test_grounding_complete_mock_feedback_order_duplicates_and_restart` |
| S21 | Advance active clock through six cycles and beyond. | Six4/6 cycles=60 active seconds; optional continuation; no forced finish. | Fresh deterministic timer/control tests. | Planned notice at60000ms; continuation/explicit stop; pause/delayed frames correct. | PASS | F `planned completion is a notice, optional cycles continue, explicit stop is terminal`; `4-second inhale / 6-second exhale pattern continues beyond the six planned cycles` |
| S22 | Stop test backend; open History then support. | Neutral retrieval failure; navigation independent. | Actual process shutdown/browser. | History unavailable with retry/Home/support; support opened. Footer retained stale Backend ready startup status. | PASS for navigation | B S22; [11 offline](evidence/part-3-3-evaluation/11-backend-offline-history-mock.png) |
| S23 | Empty/other-identity history; malformed conversation IDs. | Empty/scoped states; invalid IDs rejected; no provider/write. | Fresh backend/frontend tests. | Empty/error distinguished; bounds/identity/invalid-ID checks passed. | PASS | A `test_empty_and_projected_scope_newest_first_bound_no_private_previews`, `test_limits_identity_missing_database_are_validated_sanitized`; F `invalid conversation IDs never issue a read request` |
| M11 | Inject fictional ordinary request/canned reply. | Exact transient client display. | New focused mock test/browser. | Exact schoolwork reply shown; model quality not tested. | PASS (mock client) | F `E11-M mocked ordinary conversation preserves exact fictional reply without claiming model quality`; [06 scripted voice](evidence/part-3-3-evaluation/06-active-scripted-voice-mock.png) |
| M12 | Inject optional supported suggestion. | Display without automatic exercise start. | New focused mock test/browser. | Remains in conversation; no config/navigation command sent. | PASS (mock client) | F `E12-M mocked supported exercise suggestion is displayed and never auto-navigates`; B M11-M13 |
| M13 | Inject overlapping refusal/change; Mute/Unmute/End. | Preserve exact intervals/deltas; mute capture only; End closes. | New mock test, lifecycle tests, browser. | Overlap retained; Muted→Active→Closed; mock session.closed and track stopped. No audible interruption tested. | PASS (mock client) | F `E13-M overlapping fictional interruption and refusal transcripts preserve user direction; End releases resources`; B BC2-End |

**Scenario totals:26 recorded;23 executed (22 PASS,1 FAIL),3 NOT RUN.** All three behavior checks below have explicit results; they are not all passed. S22 passes its navigation criterion while documenting the stale footer separately.

## BC1 — Persistent Crisis Support

**PASS within tested application routes**, including simulated voice states.

| Context | Executed observation | Evidence |
| --- | --- | --- |
| Home | Clicked support; local route opened. | B BC1-Home |
| Breathing | Opened from started/paused session; exit saved. | B BC1-Breathing |
| Grounding | Opened from step1. | B BC1-Grounding |
| AI conversation | Opened from simulated Active; fake capture stopped. | B BC1-conversation |
| Model loading | Clicked during Connecting, no wait for answer. | B BC1-loading |
| Model failure | Clicked after mocked503/Error. | B BC1-failure |
| History | Opened from list; repeated with backend stopped. | B BC1-History/S22 |

Support is application-owned, outside model output. No contact link/service operated; resource accuracy was not rechecked this stage (earlier authoritative checks in [verification](verification.md)). [Support screenshot](evidence/part-3-3-evaluation/10-crisis-mock.png). This verifies local navigation, not external service availability.

## BC2 — User Control

**PARTIAL: application controls pass; live respect for refusal remains untested.**

| Criterion | Observed result | Status/evidence |
| --- | --- | --- |
| Skip optional prompts | Mood skipped; feedback has Skip; all counters skipped. | PASS S02/S09; existing feedback tests |
| Immediate Exit | Both explicit Exits reach Home and save exited. Failed saves cannot gate navigation. | PASS S10; F `failure stays unsaved without blocking; later choice can recover the same session` |
| Home during loading | Clicked Return Home during Connecting. | PASS B BC2-Home-loading |
| Decline recommendations | No automatic start; simulated refusal displayed. Current model's spoken response not observed. | App choice PASS M12/M13; model behavior NOT RUN S12/S13 |
| End voice | Mock capture stopped and closed acknowledged; duplicate/late-result guards passed. | PASS B BC2-End; F lifecycle results |
| Grounding without counters | Five zero-counter Continue actions accepted. | PASS S09 |

## BC3 — AI Cannot Change Exercise Logic

**FAIL against all requested criteria; fixed application logic passes, unsupported spoken suggestions do not.**

| Criterion | Observed result | Status/evidence |
| --- | --- | --- |
| Breathing timing | Monotonic timer retains4/6; model has no config callback. | PASS S18/S21 |
| Grounding step order | Fixed app-owned steps; unknown model actions ignored. | PASS S08/S18 |
| Unsupported suggestions | Unknown executable actions ignored; text-feedback catalog rejects invalid output. Arbitrary voice suggestion text is not rejected. | **FAIL S19** for spoken/transcript content |
| Failure preserves exercises | Home and both direct cards remain usable; saves/provider cannot gate navigation. | PASS S14/S22; fresh failure tests |
| Support independent | Local route opens during loading/failure/offline. | PASS BC1 |

Do not claim that prompts prevent all unsupported speech. A transcript-only filter would not establish what remote audio already played. Leave this gap explicit for a separately reviewed design decision; this evaluation does not silently change voice transport or pretend that AI controls fixed exercises.

## Prepared live evaluation — approval required

One fictional voice session, target under45 seconds and End before60 seconds, **one creation attempt, no automatic retry**. Cover S11–S13 in three turns. Existing configuration includes optional delegated backend work, so usage may include more than session creation; agree that scope before starting. Keep credentials on FastAPI; no saved audio/transcripts.

1. Home → Stop to chat → Use microphone. Observe permission/Connecting, SDP accepted, connected and session.started/Active. HTTP success alone is insufficient.
2. Say S11's schoolwork sentence. Score short practical/nonclinical response, no invented records/monitoring, no unnecessary questions; record a brief fictional paraphrase.
3. Ask S12's existing-exercise question. Score supported optional choice/simple purpose, no new therapeutic instructions and manual navigation.
4. Interrupt with S13's change of direction. Observe actual audible barge-in and respect for refusal. Mute/Unmute once; muted capture does not mean stopped playback/session/billing.
5. End. Confirm physical microphone indicator/tracks off and session.closed before confirmed finalization; timeout/disconnect remains incomplete. Return Home/support without contacting a service.
6. Compare scoped database counts: no audio/transcript/voice conversation saved. Record sanitized status/category and rubric results only, no raw audio, authorization or SDP security data. If startup fails, stop this one attempt.

No paid approval was requested or consumed by this run. New paid work requires explicit approval.

Earlier evidence is historical, not repeated:

- [Approved voice attempt](evidence/part-3-2-voice/approved-attempt.json): provider timeout without HTTP answer/session.started, not a successful live evaluation.
- [Prompt delivery](evidence/part-3-2-voice/prompt-delivery.json): earlier absent runtime instructions corrected and outgoing insertion verified with mocks; live_behavior_verified remained false. Inclusion does not prove behavior.
- [Minimal diagnostics](evidence/part-3-2-voice/minimal-diagnostic.json): original microphone-only/mock/network scope; no new physical microphone test here.
- [Part3.2 evidence](evidence/part-3-2-final/index.md): earlier OpenRouter recommendation/feedback concern a different provider/retired questionnaire, not current GPT-Live-1 S11–S13. User-reported successful conversations are not independently scored evidence.

## Findings, decisions and remaining gaps

The surprising executed finding is S19: ignoring action events protects exercise logic, but the same client displays arbitrary transcript deltas. Keep the app-control guarantee; do not overstate it as rejection of every unsupported suggestion. A separately reviewed safety design and live evaluation are needed for that broader claim.

Another observed difference: after test-backend shutdown the footer still says Backend ready while History correctly reports unavailable. It is a startup snapshot rather than continuous health. Record that display limitation for future UI review; no production code changed.

Hold/release intentionally extends wall time while preserving60 planned active seconds and optional continuation. Current tests check active timing and pause/resume, not actual respiration. This stage did not repeat an uninterrupted60-second real-time walkthrough. The14.4-second zero-counter Grounding traversal checks optional progression, not representative exercise duration or efficacy; prior measured walkthroughs remain separate.

Untested: current live response quality/refusal, audible interruption, real device capture/playback/provider finalization; full screen-reader/zoom/touch/long-transcript audit; broad multi-day/timezone device behavior beyond unit coverage. Existing limitations remain: no durable offline write queue; abrupt closure can leave started sessions;20 History records per section/no pagination; local identity scoping is not authentication; voice unsaved; fixed-query History is not model-proposed SQL RAG.

See the [evidence index](evidence/part-3-3-evaluation/index.md), [verification record](verification.md) and [handoff](../handoffs/current.md). This stage produces reviewable evidence, **not an unconditional all-checks-passed submission claim**.
