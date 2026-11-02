# Research-to-design mapping — current application and history

R1–R4 and D1–D6 are attributed to the **instructor-provided Assignment 3 study summary (IST 402 course material)**. The following is design reasoning, not independent research citations or proof of clinical effectiveness.

## Current mapping — November2, 2026

| Instructor input | Implemented decision and tradeoff | Evidence/limit |
| --- | --- | --- |
| R1: Short guided duration | Breathing plans six4/6 cycles=60 active seconds; Grounding estimates70s with manual progression. Setup, pauses and optional continuation are separate. | Actual sessions can exceed90s by user choice; no forced completion. |
| R2: Accessible safety | Local Crisis Support remains available independently of backend/models. | Tested routes/failures; external resource checks retain their original dates. |
| R3: Stop/skip permission | Mood/feedback/counters optional; immediate Exit and voice End; Breathing can pause. | Speech respect for refusal is not yet scored. |
| R4: User journey control | Both skills direct; manual Continue/Back/Finish; AI cannot auto-start a skill. | Choice/interaction is not evidence of correct breathing or emotional state. |
| D1: Lower interface burden | Stable layout and direct conversation remove the old Simplify toggle/questionnaire. | Adaptive progressive contraction is not implemented; do not claim it is. |
| D2: One action/instruction | One fixed phase or sensory step; no combined exercise dashboard. | Voice content is less predictable than app-owned instructions. |
| D3: Low emotional cost | Neutral language, skippable check-in, no required typed disclosure or scores. | A skipped marker can be saved; it is not an emotion. |
| D4: Persistent safety | Shared header plus an in-dialog action; local route during model/save failure. | No classifier or generated decision controls access. |
| D5: Personalization without setup | Recently used uses latest completed supported exercise; card order unchanged. | No mood-based sorting, reset/preferences UI or new AI context from History. Existing text feedback may use optional mood plus up to3 scoped summaries. |
| D6: Calm/accessibility | Muted palette, large labeled buttons, focus and reduced-motion alternative. | Limited rendered checks passed; full screen-reader/zoom/device checks remain pending. |

These are interpretations of the instructor study summary, not clinical findings. Current [design](design.md), [flow](user-flow.md), [evaluation](evaluation/scenarios.md) and [verification](verification.md) are authoritative. The following dated revisions preserve earlier decisions and failed/revised approaches.

## Revised design approach — October 19, 2026

Historical Grounding-only milestone; later current controls/data and History supersede older scope statements.

STOP was initially selected because it was easy to implement. Developer review found its four reading-oriented instructions too passive. **5-4-3-2-1 Sensory Grounding** now replaces it in active selection: users can tap observable progress through the five supplied senses without typing/describing observations. This change is a documented revised design approach for AI-use/development evidence; exact instructions and the decision came from the developer, while implementation/migration/testing used the coding agent. It does not establish that Grounding improves mental health more than STOP.

| Assignment input | Current implementation and rationale | Tradeoff / verification |
| --- | --- | --- |
|R1: Short guided duration|20/15/15/10/10-second assumptions total 70 seconds, within the 60–75-second home estimate. Record actual duration and separate setup.|No forced timer; user pauses may exceed 90 seconds. Measure a fictional walkthrough; distinguish estimate from observed time.|
|R3: Permission to stop or skip|Continue with zero/partial circles skips without penalty; Exit is immediate at all five senses.|No completion score or enforced noticing count. Verify zero-circle progression and every Exit.|
|R4: User control|Manual Continue/Back, reversible taps, earlier progress preserved, no automatic advance.|User chooses pace; transient progress resets on restart. Verify undo and backward navigation.|
|D2: One action at a time|One exact sensory instruction and its circles at a time.|Instruction plus circles still adds visual load; mobile layout/focus review required.|
|D3: Minimal emotional and interaction cost|Optional tap-only progress; no descriptions, disclosures, required fields or explanations.|Some senses may be unavailable/uncomfortable; skip is equally valid and requires no reason.|
|D6: Clear, neutral instructions|Developer-supplied “Notice…” copy, checkmark/text progress, restrained colors and large labeled buttons.|Counts describe selections only, never clinical improvement or emotional interpretation.|
|R2 / D4: Independent safety|Existing persistent support header/modal access stays independent of model/backend.|Verify all five steps, not just home.|
|D1 / D5: Low burden and user-led personalization|Stable equal-choice cards retained; mood never blocks either exercise. Simplify toggle removed at developer request.|No new personalization inference or configuration.|

The intended 70-second path is a hypothesis; actual measured duration is reported in [verification](verification.md), including voluntary review pauses/tool overhead. No new clinical citation is invented. The [current design](design.md) and [revised mockups](mockups/grounding.html) supersede STOP only in active exercise choice. Historical sessions/conversations and original mockups remain intact.

## Historical Help Me Choose — developer-requested refinement

Superseded October26 by direct conversation; preserved for design provenance.

The original two-card proposal kept AI outside selection. Review now asks for a meaningful but optional suggestion, without mandatory typing or a questionnaire. The model can choose between supported skills using an explicit focus and limited saved self-report/activity. This is a revised design approach recorded for AI-use/development evidence, not a new clinical research finding.

| Assignment input | Refinement | Tradeoff / check |
| --- | --- | --- |
| R1 / D2 | Three focus buttons, one suggestion and one brief reason; exercises still have the same intended duration. | Model latency is separate entry/selection time, never part of exercise timing. Test immediate manual start/Home during loading. |
| R3 / R4 | Optional card; direct skills stay on Home; Start Suggested and Choose Other require explicit taps. | Suggestion may influence choice; label the alternate and never auto-start or restrict access. |
| D1 / D3 | Tap-only selection and bounded contextual data, no descriptions or required setup. | Saved mood can be sensitive. Disclose its optional use, omit skipped mood, send no identities or free text. |
| D4 | Shared independent support in selection/loading/failure/exercise/completion. | Preserve route despite any model/database error; test actual browser failures. |
| D5 | Explicit focus, optional mood and at most three recent supported sessions. | Activity is not a diagnosis or outcome measure; model cannot infer clinical benefit. Scope/review the snapshot and keep both choices. |
| D6 | Supported exercise enum and reviewed neutral reasons/replies, truthful mock/live/static labels. | Limited expression is deliberate; reject unreviewed output and retain manual choices. |

R1–R4/D1–D6 remain from the instructor-provided Assignment 3 study summary. No external clinical citations or effectiveness claims are added. Details are in design.md/design-pipeline.md and actual results in verification.md.

## Original Part 3.1 research mapping and inspected patterns — historical

The material below preserves the original proposal and its alternatives. STOP and future-tense implementation/provider statements describe that original milestone; current implementation/contracts and later live verification are in design-pipeline.md and verification.md.

# Original research-to-design decisions

**Source attribution for all R1–R4 and D1–D6 below:** instructor-provided Assignment 3 study summary (IST 402 course material), as supplied in the assignment instructions. These requirement/principle labels are carried over from that summary; the interface choices, alternatives, and tradeoffs are Pause’s design interpretation. No external study authors, titles, dates, or citations are inferred. The course summary is a design input, not evidence that Pause is clinically effective. The underlying original studies have not been independently reviewed. If a formal course-material bibliography entry is required, use the instructor’s actual title/date rather than inventing missing metadata. Detailed behavior is in [design](design.md); navigation is in [user flow](user-flow.md).

| Input | Decision and influence | Alternative and meaningful tradeoff | Future verification |
| --- | --- | --- | --- |
| R1: Under 90 seconds | Breathing is six fixed 4/6-second cycles (60 seconds); STOP intended path is 48 seconds reflection + 8 seconds taps + ≤4 seconds delays (about 60 seconds). No model wait in exercises. | A hard time limit would restrict autonomy. User dwell/backtracking may exceed 90 seconds; the guided path, not every session, meets the target. | Measure first-instruction-to-final-step duration including delays, and report entry/setup separately; controlled-clock breathing test. |
| R2: Frictionless crisis access | Visible labeled Crisis support on every state; static route works without AI, database, login, or mood response. Dialog includes its own button. | A hidden menu reduces visual load but adds discovery/navigation cost. Always-visible access consumes header space. | Check all screens, modal, offline/backend failure, and pending/rejected model output. |
| R3: Permission to leave | Persistent Exit returns home immediately; “You can stop at any time”; no early-exit feedback demand. | Confirmation could prevent accidental exit but adds friction. Immediate exit loses exercise progress; restarting is deliberate. | Exit every breathing phase and STOP step; no confirmation or model wait. |
| R4: User journey control | Both skills available for every mood; Skip, Back, manual Next/Finish, optional feedback/model response, and reversible simplification. | Automatic recommendations/advancement could reduce choices but undermine agency. Stable choices leave users to select a skill. | Every mood reaches both skills; Skip and Back preserve control. |
| D1: Progressive interface contraction | Earlier Simplify toggle removed at developer request; Home retains a single consistent layout with labeled cards. | A second presentation mode added an unnecessary choice; progressive contraction is not implemented in the current interface. | Preserve readable labels, direct exercise access and persistent safety controls. |
| D2: One atomic skill at a time | One exercise per session, one breathing phase or STOP instruction visible at a time. | A combined dashboard exposes more content but raises reading/navigation load. Sequential steps obscure later instructions until Next. | Walk the phase/step sequence and screen-reader announcements. |
| D3: Minimize emotional cost | Neutral language, no streaks/scores, optional mood/feedback, no forced disclosure or exit explanation. | A daily mood popup still interrupts access even with Skip. Keep it one action to dismiss and once per local day; consider removing it if coursework permits and usability evidence supports removal. | Count taps and test dismissal, storage failure, and repeat visits. |
| D4: Persistently visible safety | Shared safety header plus modal action; static resources and neutral fallbacks survive model failures. | Persistent crisis wording may feel prominent or add visual load. Use a quiet labeled button without hiding it. | Inspect all states, focus scope, contrast, and narrow-screen layout. |
| D5: Personalization without setup | Default to stable cards with “Recently used,” because minimal stored activity needs no setup. An optional mood/activity ordering policy and one-tap reset are specified in design.md; neither selects a skill nor changes access. | Automatic ordering can reduce choice effort but surprises users and has no proven mood-to-skill benefit. Stable order sacrifices ranking; a reset adds a small control burden. Mood stays out of model requests. | Check both cards for all moods/Skip, reason labels, reset, no live focus reordering, scoped data, and outbound context. |
| D6: Low-stimulus, nonjudgmental design | Quiet palette, short copy, labeled icons, large targets, gentle indicator with reduced-motion alternative. | Reduced visual novelty may be less engaging; subtle colors must still meet contrast targets. | Keyboard, zoom, contrast, motion preference, and fictional usability walkthrough. |

## Patterns inspected from Expedia Lite

At the original project inspection, the Assignment 3 directory contained only Git metadata; there were no components to preserve or reuse locally. The adjacent Expedia Lite README and the file paths listed below were inspected as read-only pattern references at that milestone. They belong to a separate project and are intentionally not repository-relative hyperlinks: a standalone Pause checkout does not contain them. No private source content or travel data is reproduced. The later authorized provider configuration is documented separately; this historical design inspection did not copy credentials.

| Inspected evidence | Pattern to adapt later | Boundary for Pause |
| --- | --- | --- |
| `frontend/src/api/travel.js` (separate-project reference), `frontend/package.json` (separate-project reference), `backend/main.py` (separate-project reference) | Vue API client separated from FastAPI routes; frontend/backend organization. | Design smaller skill views with a shared safety header; travel forms, booking UI, maps, and menus are irrelevant. |
| `backend/database.py` (separate-project reference), `backend/database_controller.py` (separate-project reference) | SQLite connection helper, foreign keys, initialization, and backend data access. | Use a new minimal schema and synthetic data; copy no travelers/accounts or travel history. |
| `backend/bi_controller.py` (separate-project reference) | Backend-only model client with bounded requests, safe errors, and injectable/mocked provider boundary. | Initial optional feedback uses approved neutral responses. For the later required RAG capability, adapt the validated read-only retrieval boundary with a new scoped schema, never unrestricted travel SQL. Navigation/instructions remain deterministic. |
| `backend/config.py` (separate-project reference) | Explicit environment loading from a known path and internal credential access; adapt the target to Pause’s backend/.env. | Choose provider later; no actual secrets read or copied. Never expose keys through frontend environment variables. |
| `AGENTS.md` (separate-project reference), `backend/test_bi_controller.py` (separate-project reference), `README verification` (separate-project reference) | Backend tests, mocked model failures, frontend lint/build, manual flow and restart-persistence checks. | Write checks for Pause requirements once implemented; previous project's reported passes are not Pause test results. |

## Other tradeoffs

Historical Part3.1 planning notes: backgrounding now pauses Breathing rather than ending it, History is implemented, and the old ordering/reset proposal is not current.

A once-daily popup gives a lightweight signal but adds friction, stores a potentially sensitive self-description, and can break its daily guarantee if browser storage is unavailable. Keep Skip visible, record no mood for Skip, and prefer access over repeated prompts. Stable card order reduces relearning at the expense of stronger recommendation personalization.

Ending an exercise when crisis information opens or breathing is backgrounded prevents silent timing drift and competing guidance. It also loses progress; the return path is home and a fresh start. Optional AI adds latency, cost, privacy concerns, and semantic risk with little value to navigation; an approved-response allowlist limits expressiveness but makes the initial response boundary reviewable. Static fallbacks remain usable without credentials. Local saved history supports the future rubric but creates retention/deletion obligations; its review UI stays in Part 3.3.


## Rationale clarification for this review

The row alternatives explain why the selected approach is preferred: R1 trades a forced timer for a short intended path; R2/D4 accept persistent header space to remove navigation/model dependence; R3/R4 preserve exit and choice over progress protection or automation; D1 uses explicit simplification because distress cannot be inferred; D2 reduces simultaneous reading; D3 accepts a skippable daily interruption while avoiding required disclosure; D5 limits data and preserves stable default choices; D6 accepts less visual stimulation while requiring readable contrast. These are design hypotheses requiring later verification, not measured outcomes. No new research source or clinical claim is introduced.


### October 22 closed-loop refinement

Historical Hold/Tap/Observe approach, superseded by October26 hold-to-run; automatic completion described here is not current.

Developer-requested button-state feedback supports D2/D3 observable action/response and D5 user control: immediate neutral cues, alternative Tap/Observe, no forced repeats. D4/D6 safety and access remain independent of tracking/model failures. This is an interface-design rationale mapped to the instructor Assignment3 study summary, not evidence that button timing establishes correct breathing or clinical effectiveness. Added interaction/choice burden is mitigated by Observe and unchanged automatic60-second completion.


## Hold-to-run Breathing refinement — October 26, 2026

The developer replaces three modes/automatic start with one primary hold control, immediate pause on release and explicit Finish. This reduces setup/choice burden (D1/D3) and makes action/result visible (D2), while native Start/Pause, reduced motion and independent Exit/support protect access and autonomy (R3/R4/D4/D5). Planned six4/6 cycles=60 active seconds meets the intended under90-second path (R1); pauses and optional continuation can extend a person's actual wall duration. Timing is not evidence of respiration, success or clinical effectiveness. R1–R4/D1–D6 are instructor-provided Assignment3 study-summary labels, not external clinical citations.

Tradeoffs: sustained press can fatigue users; the accessible alternative avoids it. Early Finish now records completed without asserting six cycles, so separate active/cycle fields are necessary. A static reduced-motion visual and textual countdown remain available. Historical schema6 fields and original Part3.1 mockups are preserved as history; the current hold flow supersedes automatic completion/background exit descriptions above. Actual checks are in [verification](verification.md) and [evidence](evidence/part-3-2-hold-breathing/index.md).


## Direct conversation refinement — October26

The developer replaces the predefined questionnaire with the existing AI conversation so suggestions can arise naturally in context. Direct Home exercise access and manual choice preserve R3/R4 user control; removing a separate focus/suggestion workflow reduces D1/D3 setup/reading and D2 competing choices. The Home label uses the developer’s browser wording, stop to chat / Ai assistant conversation; the page title Talk to Pause makes the destination explicit. Existing persona and nonclinical boundaries remain unchanged. R1–R4/D1–D6 are instructor-provided Assignment3 study-summary labels, not evidence of clinical effectiveness.

Tradeoffs: open conversation is more flexible but depends on microphone/audio/network and has less predictable replies. No new paid-model behavior is claimed; voice lifecycle uses mocks and existing integration. The developer explicitly kept voice and existing post-exercise text feedback rather than adding typed chat. Both exercises remain independently usable, support stays independent, historical recommendation data is retained, and no voice transcripts/audio are persisted. See [verification](verification.md).


## Part3.3 History and lightweight personalization — November1, 2026

User-requested History makes previously saved activity inspectable (D4/D5 control/transparency) without adding a questionnaire or required configuration (D1/D3). Neutral completion/exit/unfinished labels and separate active/wall durations distinguish observed app activity from self-report or interpretation; no emotional/clinical inference follows from counts or feedback. Home’s optional label uses the latest completed current exercise; both cards remain equal and unchanged. Generic previews avoid exposing message/mood text on the list, while explicit opening reveals the owner’s actual saved conversation. R1–R4/D1–D6 retain their attribution to the instructor-provided Assignment3 study summary; this is an interface rationale, not clinical-effectiveness evidence.

Tradeoffs:20 items per section avoids unbounded payloads but older records require future pagination; no records are deleted. Local UUID scoping has no account recovery/authentication; clearing storage changes the accessible scope. Voice remains transient, so it is absent from History. Message content is escaped rather than interpreted as instructions. Read failures omit Home personalization and keep navigation/support available. No new information goes to a model provider, and no skill timing changes. Actual test/API/SQLite/browser results are in [verification](verification.md).
