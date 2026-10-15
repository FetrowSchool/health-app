# Pause design specification

## Purpose and scope

Assignment 3.1 specifies five screen types for a coursework prototype. STOP uses four states within one screen type; crisis information is a shared auxiliary route. No working application is implemented. Visible shared copy: “Coursework prototype — not a mental health support service.” Pause does not diagnose, provide therapy, or monitor users. Research inputs R1–R4 and D1–D6 are attributed to the **instructor-provided Assignment 3 study summary (IST 402 course material)**, as supplied in the assignment instructions, and mapped in [research decisions](research-decisions.md). Navigation is in [user flow](user-flow.md).

## Shared layout and interaction

Use a narrow mobile layout that reflows on larger displays, a quiet warm background, dark text, restrained accent colors, generous spacing, and no flashing, celebratory animations, streaks, scores, or judgmental success labels. A shared header shows Pause and a top-right text button, “Crisis support,” on every state. Keep it visible without scrolling and outside disabled/loading content. Exercise views also show “Exit” prominently; exit returns directly home without confirmation or forced feedback.

Normal navigation uses labeled buttons and requires no typing or account setup. Both exercises always remain available. Home offers a small labeled “Simplify view” toggle: it hides decorative icons and secondary explanations but preserves exercise names, durations, navigation, safety, and progress. Its reversible preference is local. Never infer simplification or distress from mood, behavior, or model output.

Accessibility targets: touch targets at least 44 × 44 CSS pixels; ordinary text contrast at least 4.5:1; large text and essential graphics at least 3:1; visible keyboard focus; semantic headings/buttons; text labels alongside icons; 200% zoom and narrow-width reflow. These are proposed acceptance targets, not a claim of audited compliance. Avoid color-only instructions. Respect OS reduced-motion preference and allow a direct reduced-motion choice. Announce breathing phase changes politely, not every countdown tick. Focus moves to the new screen heading after navigation.

## Screen 1 — Daily Mood Check-In

On the first opening of a local calendar day, show a dismissible dialog over home with “How are you feeling right now?” Four large choices pair text with simple line icons: Calm (still water), Okay (level face), Anxious (wavy line), Overwhelmed (overlapping waves). No icon alone conveys meaning. Include visible “Skip”; Escape or an explicit close action counts as Skip. A single selection submits and closes immediately.

Answering or skipping records a local dismissal marker keyed by pseudonymous local profile and device-local YYYY-MM-DD, synchronously before persistence requests. Reloads that day must not reopen it; a later local date may show it again. Do not use a fixed 24-hour interval or server UTC date. Time-zone changes follow the current device date; previously dismissed dates remain dismissed. Repeated tabs synchronize dismissal where supported. If browser storage fails, suppress repeat prompts within the current visit and permit navigation; cross-reload once-per-day behavior then cannot be guaranteed. Database failure must not reopen the popup.

The dialog includes its own visible “Crisis support” action inside its focus scope; do not rely on the obscured background button. Trap focus accessibly, restore it on dismissal, and allow crisis navigation immediately. Opening crisis information dismisses the popup as a Skip, so returning home does not prompt again that day. Mood is an optional self-description, never an assessment or distress detector. A Skip row stores no mood value.

## Screen 2 — Home

Top: Pause, Crisis support, and concise coursework label. Heading: “Take a moment.” Two full-width, one-tap cards: “Paced Breathing — About 60 seconds” with a breath-circle icon; “STOP Exercise — About 60 seconds” with a pause-hand icon. Include “Simplify view” without introducing a menu hierarchy. No mood gates, required recommendations, or forced exercise choice. Optional lightweight personalization can add a small “Recently used” label to a card; keep positions stable and both cards equally actionable.

## Screen 3 — Paced Breathing

Show a large gently expanding/contracting circle, “Breathe In” or “Breathe Out,” remaining phase seconds, and “Cycle 1 of 6” plus a simple six-part progress indicator. Always show Exit and Crisis support. A short static note says “You can stop at any time.”

Fixed sequence: inhale 4 seconds, exhale 6 seconds, repeated six times: (4 + 6) × 6 = 60 seconds of guided activity. Begin when the exercise view is ready; any short loading delay is outside the guided timer and must remain within the end-to-end budget below. No holds, altered cycles, or AI timing. Future Vue code derives phase and progress from monotonic elapsed time rather than accumulating interval ticks. Reduced motion replaces circle scaling with a static circle, phase label, countdown, and discrete progress changes; timing is identical.

Measure R1 from first instruction through the final planned phase, including application delays: the nominal guided sequence is exactly 60 seconds. Separately target entry/setup and completion transition overhead ≤ 2 seconds total, yielding approximately 62 seconds from selection through completion. These are targets, not measured results. Completing the six planned cycles may show completion, but no timeout forces a user to leave the screen; Exit remains available throughout. No network or AI wait is needed to start or finish. On backgrounding or opening crisis information, end the active session as exited/interrupted and return home after the interruption; never silently skip unseen phases or resume automatically. A new selection restarts all six cycles.

## Screen 4 — STOP Exercise

Display one supplied instruction at a time:

| Step | Heading | Instruction | Controls |
| --- | --- | --- | --- |
| 1 | Stop | Pause what you’re doing. | Next, Exit, Crisis support |
| 2 | Take a Step Back | Give yourself a moment before reacting. | Back, Next, Exit, Crisis support |
| 3 | Observe | Notice what is happening internally and externally. | Back, Next, Exit, Crisis support |
| 4 | Proceed Mindfully | Consider what you want to do next. | Back, Finish, Exit, Crisis support |

Use “Step 1 of 4” and four discrete segments. Finish is the final Next action and leads to completion. Back changes the visible step without starting a second session. No countdown, forced advancement, or automatic exit. Users may leave instantly or dwell as long as they choose.

Timing assumption: roughly 4 seconds reading plus 8 seconds reflection per step (48 seconds total), four forward taps at roughly 2 seconds each (8 seconds), and up to 4 seconds total rendering/transition delay: approximately 60 seconds. The intended guided path is therefore below 90 seconds. Extra reflection, repeated Back use, interruptions, or accessibility needs can exceed 90 seconds of wall-clock time; R1 is a guided-path design target, not a limit imposed on users. Validate these assumptions with fictional walkthroughs before claiming measured compliance. Persistence/model requests must not delay progression.

## Screen 5 — Completion and Optional Feedback

Neutral heading: “Exercise complete.” Buttons: Helpful, Not Helpful, Skip. Separate “Return home” is always available and does not require feedback. Return home without selection is stored as skipped feedback; do not label it Not Helpful. No feedback popup follows an early Exit. Crisis support and coursework labeling remain visible.

After a feedback choice, optionally offer “Show a brief response.” This is opt-in and remains on the completion screen. A pending request never disables feedback, Return home, or Crisis support. The model receives only the exercise identifier and feedback enum; Skip sends no mood or history. Prefer a response under 40 words, at most two sentences, acknowledging the choice without therapeutic advice, diagnosis, efficacy promises, new exercises, or altered instructions. Example static fallback: “Feedback noted. You can return home whenever you choose.”

Backend request timeout proposal: 5 seconds; malformed, empty, disallowed, or failed outputs use the fallback. Length/schema validation alone cannot ensure semantic safety. For the initial implementation, use a reviewed allowlist of short neutral responses and accept generated output only if it matches an approved response; otherwise use fallback. Do not append raw rejected output to the UI or logs. Broader free-form generation requires a separate safety review and is an unresolved future scope decision.

## Independent crisis-support route and fictional input

Crisis support opens a locally bundled information view from every screen, including modal, model pending/failure, and database error states. Opening it during an exercise immediately ends that session as interrupted; its “Return home” button never resumes an exercise. From completion it returns to completion with feedback preserved; from home/mood it returns home. Shared coursework copy remains visible. No model call, login, mood answer, or persistence success is required.

The initial prototype will display **U.S.-specific 988 Suicide & Crisis Lifeline information**, independently of the model. Proposed static copy: “U.S. crisis support: call or text 988, or visit 988lifeline.org for online chat. These resources serve the United States and its territories; they are not a worldwide resource. Outside this region, use crisis resources for your location. Pause is a coursework prototype and does not provide or monitor support.” Show the geographic limitation alongside the contact details, not behind another menu; do not infer location or route based on mood. The existing five mockups represent the entry button only, not this auxiliary resource view.

Resource information verified online on October 15, 2026 against the service operator’s [About 988](https://988lifeline.org/about/) (U.S./territory coverage and round-the-clock availability) and [What to Expect](https://988lifeline.org/get-help/what-to-expect/) (call, text, and online-chat channels). These sources verify external resource information, not Pause’s effectiveness or functioning navigation. No call, text, chat, or contact with a person was initiated. A separate SAMHSA FAQ fetch returned HTTP 403, so it is not represented as successfully inspected.

Future controls may offer tap-to-call/text and a chat link plus readable plain-text details. Bundled information stays readable without backend/model availability; external calls/texts/chat require compatible device/network services and are not operated by Pause. Do not promise connection speed, universal international availability, or real-time monitoring by the prototype. Recheck official information before implementation/submission if delayed, date the resource content, and maintain it separately from prompts. Any additional emergency-service guidance must be verified separately before inclusion.

There is no free-text input in the initial five-screen journey. For a possible later fictional conversation test, an explicit crisis-support button always works; a simple backend rule may match a small set of explicit crisis-related phrases and return approved static resource copy, bypassing model generation. Ambiguous input gets a neutral static response plus the same crisis route. Matching can miss slang, negation, languages, or indirect statements and can trigger on fictional/quoted text; do not call it triage, assessment, monitoring, or reliable detection. No automatic emergency contact, location collection, distress score, or implication that staff are watching. False positives/negatives, provider failure, and prompt injection are synthetic test cases. Do not store an inferred-risk label or use mood as a substitute detector.

## Proposed architecture

- Vue: shared safety header, mood dialog, home cards, deterministic breathing controller, four-state STOP view, completion feedback, and static crisis information. State changes are immediate; network writes run separately with clear neutral save errors.
- FastAPI: typed validation, session/mood/feedback endpoints, database service, model-response service, configuration, and safe errors. Never expose provider keys to Vue. No model tool execution. The initial feedback path needs no retrieval SQL; later assignment RAG may accept only validated, scoped, read-only model-proposed SQL as described below.
- SQLite: local persistence only through backend transactions and parameterized queries. Generated runtime file is `data/app.sqlite3`, resolved from the project root rather than the working directory, and stays untracked. Enable foreign keys; design versioned migrations and idempotent initialization in Part 3.2.
- Model: conversational provider behind FastAPI. Planned backend variables `MODEL_API_KEY`, `MODEL_NAME`, and optional `MODEL_BASE_URL`; select provider later. Never put keys in frontend `VITE_*` variables. Explicitly load future `backend/.env`; future `backend/.env.example` uses placeholders. Add `.gitignore` protections before secrets/runtime files; environment files do not exist yet.

No endpoint, table, component, migration, prompt, or environment file is implemented now. Proposed API responsibilities: accept optional daily mood/skip, create/update exercise sessions, record optional feedback, and request opt-in response; later read saved sessions/conversations. Validate enums and profile ownership and avoid sending entire records to the provider. Offline/static navigation remains usable even if a record cannot be saved. Retry writes with an idempotency key; failed saves must not be presented as durable history.

## Proposed database design

Use a generated local pseudonymous profile, not names, emails, passwords, precise locations, or clinical demographics. Single-device classroom use is the initial assumption; this is not production authentication.

| Table | Proposed fields and constraints | Purpose |
| --- | --- | --- |
| local_profiles | id PK, created_at UTC | Separates local demo records without identity data |
| mood_checkins | id PK, profile_id FK, local_date, timezone_name, outcome answered/skipped, mood nullable enum, recorded_at UTC; UNIQUE(profile_id, local_date) | Once-per-day optional mood record; answered requires one of four moods; skipped requires NULL |
| exercise_sessions | id PK, profile_id FK, exercise breathing/stop, started_at UTC, ended_at nullable UTC, status in_progress/completed/exited/interrupted, feedback nullable helpful/not_helpful/skipped, duration_seconds nullable nonnegative | Completion and minimal activity; null feedback means not yet offered/recorded |
| conversations | id PK, profile_id FK, session_id nullable FK, created_at UTC, updated_at UTC | Optional completion-response thread and future conversation grouping |
| messages | id PK, conversation_id FK, request_id, ordinal, role user/assistant, content, created_at UTC, source structured_feedback/model, request_status pending/succeeded/failed/rejected; UNIQUE(conversation_id, ordinal), unique idempotency key per submission | Ordered submitted button-context messages and actual approved model replies; failure records never fabricate assistant content |

Profile ownership must match across linked sessions and conversations, enforced by service validation and appropriate composite relationships. CHECK constraints enforce enums and status/end-time consistency. Foreign keys cascade when deleting a profile/conversation; session deletion may cascade linked conversations to avoid orphaned sensitive content. Session feedback stays NULL after early exit. An unfinished persisted session found after restart is marked interrupted, never completed. Store timestamps for activity, not detailed click streams or every countdown tick.

Conversation/message creation happens only for opted-in saved responses. Save the submitted structured user message and actual approved model reply with request status. A failed/rejected request retains the submitted message with failed/rejected status and no fabricated assistant reply. Static fallback is UI copy, not an actual model reply and is not saved as one. Never retain raw rejected generations, provider secrets, or hidden reasoning. Return accurate saved/unsaved status; a database failure leaves the displayed response explicitly unsaved. Retry with the same submission key to prevent duplicates, ignore stale responses after leaving, and do not silently repeat provider calls. Provide a clear note about what is saved and what minimal context is sent externally before model opt-in. Retention proposal: retain local synthetic records for the assignment demonstration, provide deletion in future history review, and clear fixtures after assessment. Confirm duration and deletion UI with the assignment owner. SQLite is not automatically encrypted; do not claim production confidentiality.

Personalization queries previous completed sessions and feedback to add “Recently used” or suppress repeated optional-response offers after Not Helpful. No extra preference questionnaire, inferred diagnosis, or hidden exercise restriction. Do not personalize exercise instructions, duration, or crisis access. Stable card order remains the default represented in the mockups. Mood/activity may support the optional ordering alternative below; mood is never sent to the feedback model.

## Future saved-history review — Part 3.3

Reserve a clearly labeled “Saved activity” entry from home for a later milestone. Plan a simple chronological list of date, exercise, completion status, and optional feedback; selecting a record reveals its saved conversation messages in order. Users can review sessions with no conversation and explicitly delete records. Handle empty history and failed saves neutrally. Use the same pseudonymous profile scope, backend read endpoints, and persistent crisis button. This is a documented future feature, excluded from the initial five screens and [current flow](user-flow.md).

## Unresolved decisions and Part 3.2

U.S./territory scope and the initial 988 resource details are now selected and externally verified; recheck them before implementation. Confirm model provider and data-handling terms; retention duration and deletion controls; whether the rubric requires free-form conversation in Part 3.2 or only later; and how local profiles behave on shared devices. Confirm acceptability of the intentional interrupted-session rule and daily popup storage fallback. Research attribution is to the instructor-provided Assignment 3 study summary; do not invent underlying-study citations. Confirm any course-required bibliography metadata with the instructor.

Part 3.2 implements the agreed frontend/backend structure, accessible views, timing/state logic, static crisis route, minimal database schema, safe model integration and failure handling. Verify keyboard/focus/contrast/reduced motion, daily dismissal and rollover, independent crisis/exit paths, persistence/restarts, guided timing, and model failures with fictional data. The documentation contains planned targets, not measured usability or clinical outcomes.

## Static visual mockups

The [five-screen gallery](mockups/index.html) visualizes this specification at 390 × 844 CSS pixels using shared light-neutral, muted-blue, and gray styling. Open the HTML directly in a browser; CSS and icons are local. The gallery is documentation only: no navigation, timing, persistence, crisis service, or model integration is implemented. The completion heading was changed from “Exercise finished.” to the requested neutral “Exercise complete.” wording; behavior is unchanged.

The popup includes its own crisis button and visible Close/Skip controls. Home includes the planned Simplify view control. Breathing shows a static first-inhale state and reduced-motion control; STOP shows only step 2. The completion preview is the initial optional-feedback state, before any later opt-in response. All controls are inert visual samples but keyboard-focusable for styling review. The popup is a labeled static group, not a functioning modal or focus trap.

Review tradeoffs: the daily popup still adds friction, persistent safety occupies header space, and large readable controls limit content density. No app behavior or accessibility certification can be inferred from static frames. Real modal focus management, phase announcements, reduced motion, zoom/reflow, and interaction verification remain Part 3.2 work.

Mockup source verification: all five screen groups contain visible crisis buttons; mood/completion contain Skip; breathing/STOP contain Exit; STOP includes Back/Next. The earlier source review found all then-current Markdown links and local gallery assets resolved; see the [current verification record](verification.md) for this review. Shared CSS specifies 844-pixel frame height, up to 390-pixel width, and at least 44-pixel controls. Calculated contrast is 11.82:1 for main text, 5.47:1 for secondary text, 5.88:1 for primary-button text, 3.29:1 for control borders against the screen, and 6.81:1 for focus outlines. These checks cover the listed palette pairs, not a full accessibility audit.

Browser verification limitation: the available preview browser rejected the local `file:` URL under its URL policy. Rendered overflow, focus appearance, and zoom behavior have therefore not been verified. Inspect all five frames in a local browser at default size and at 200% zoom; fixed-height study frames may need scrolling under enlarged text. The eventual application must use flexible layouts rather than treating the mockup frame height as a content limit.

## Optional card ordering and user control

The current mockup keeps Paced Breathing first and STOP second to reduce relearning. To address mood-informed prioritization without making a clinical inference, a future explicitly optional policy could place breathing first after Anxious/Overwhelmed and the most recently completed skill first after Calm/Okay or Skip; with no completed activity use the default order. This is a proposed presentation heuristic, not evidence that one skill fits a mood or a judgment of distress. No card is selected, launched, hidden, disabled, or given a different exercise sequence. Any ordering changes occur only when entering home, never while a pointer/focus is on a card.

If adopted, show a short reason such as “Based on your check-in” or “Recently used,” plus a one-tap “Use default order” reset. No account, configuration questionnaire, or setup is required. Both equally sized cards remain visible and one tap away, and Skip causes no restriction. A small optional reset is the cost of making personalization understandable and changeable. Mood-based reordering can surprise users and has no demonstrated benefit here; adopting it requires usability review. The current stable-order design is preserved.

## Optional AI feedback contract and later RAG boundary

The model's limited contribution is conversational acknowledgment of a voluntary feedback choice. It is excluded from exercise timing and instructions because those must remain fixed, immediately available, and reviewable. Selecting Helpful/Not Helpful/Skip alone saves feedback without making a provider call. “Show a brief response” is a separate opt-in, available even after Skip; it sends exercise ID and feedback enum (including skipped) with a fixed reviewed instruction and response schema. The backend may use opaque request/conversation IDs internally, but must not send those IDs or a complete database record to the feedback provider. Exclude mood, names, contact details, precise location, free-text disclosures, full history, and inferred emotional state. Proposed provider limit is one call per explicit request, five-second timeout, no automatic retry, ≤40 words/two sentences, and the reviewed neutral-response allowlist described above.

Worked fictional example: after STOP, the user chooses Not Helpful and opts in. The structured submission is `{exercise: stop, feedback: not_helpful}`; an approved actual reply might be “Feedback noted. You can return home whenever you choose.” Save the structured submission and actual approved reply in one conversation with ordered IDs/timestamps and status. If the provider times out, the same sentence may appear as static fallback but must be identified internally as UI copy, with no fabricated model reply. Home, Exit where relevant, and crisis access remain immediate regardless of provider or storage status. Even Skip and no response are valid completed journeys.

The starter's two-call SQL-based RAG and eventual saved-history views remain required future assignment plans. They do not authorize adding free text, a history screen, or retrieval to this initial five-screen journey. Before implementation, confirm whether RAG belongs in an expanded opt-in conversation or a later saved-activity explanation. Query planning must use an allowlisted schema, restricted read-only connection, enforced local-profile/conversation scope, bound values/results/time, and a second bounded answer call using only approved retrieved fields and reviewed content. Stored text is data, never instructions. The five-second single-call feedback budget does not describe that two-call path; approve a separate finite budget and grounded-response contract first. An exact neutral allowlist cannot meaningfully explain arbitrary retrieved records, so the current feedback contract is not claimed to satisfy full RAG. Both remain backend-only and optional to navigation. Original notes prohibiting all model SQL and Expedia-specific environment loading are superseded by these scoped plans.

## Assignment 3.1 deliverable review

| Deliverable | Current evidence | Limit |
| --- | --- | --- |
| Application overview and five screen types | README, screen sections, five HTML study frames | Static design only |
| Research connections | Ten rows in research-decisions.md with specific features, reasons, alternatives, tradeoffs, and future checks | Attributed to instructor-provided Assignment 3 study summary; original studies not independently reviewed |
| User journey | Mermaid flow plus explicit skip/exit/interruption rules | Diagram and source reviewed; no running navigation |
| AI, data, personalization | Feedback contract, related schema, ordering alternative, future RAG boundary | Provider, retention, shared-device policy, and RAG milestone remain open |
| Safety and accessibility | Independent route plan, fictional-input limits, visible controls, palette/focus/reduced-motion specifications | U.S. 988 details externally verified; rendered layout, screen-reader and motion behavior remain unverified |
| Timing | Breathing 60 seconds; STOP 4 × (4 reading + 8 reflection) + 8 taps + ≤4 delays = about 60 seconds | Estimates, not measured user results; voluntary pauses may extend wall-clock time |
| Reuse and future review | Expedia Lite mapping and Part 3.3 history plan | Patterns inspected, no code copied |

No clinical efficacy or runtime compliance is established by this design review. Research attribution and U.S. 988 resource selection/source verification are now documented. The remaining Assignment 3.1 evidence item is visual/browser review of the five frames including zoom/overflow, plus instructor-specific bibliography formatting if required. Confirm response content, retention and deletion, shared-device behavior, and the future RAG/conversation milestone before Part 3.2. Parts 3.2/3.3 implementation, persistence tests, and editable Figma capture are intentionally deferred. No new interface design or working functionality was added in this review.
