# Pause design specification — current Grounding revision

## Scope and design history

Current Assignment 3.2 implementation: Paced Breathing and **5-4-3-2-1 Sensory Grounding**. The journey has the original five screen types plus a direct AI conversation screen: daily mood dialog, home, conversation, breathing, grounding, completion/optional feedback. Crisis information is a shared independent auxiliary route. The coursework label remains “Coursework prototype — not a mental health support service.” No diagnosis, therapy, clinical-effectiveness claim, monitoring, or required disclosure.

The original Part 3.1 proposal selected STOP because it was easy to implement. During developer review its four reading-oriented instructions felt too passive. Grounding replaces it with concrete, observable taps while preserving the simple interface. This is a revised design approach, not evidence of greater clinical benefit. Preserve the [original specification](history/part-3-1-design.md), [original flow](history/part-3-1-user-flow.md), and unchanged [STOP-era mockups](mockups/index.html) as history. Review the [revised Grounding mockups](mockups/grounding.html) for the current direction.

R1–R4 and D1–D6 come from the **instructor-provided Assignment 3 study summary (IST 402 course material)**. They motivate design hypotheses, not external clinical findings. See [research mapping](research-decisions.md), [current flow](user-flow.md), implementation contracts in [design-pipeline.md](design-pipeline.md), and measured evidence in [verification.md](verification.md).

## Shared interaction and accessibility

Keep the light neutral background, muted blue/gray accents, dark readable text, labeled icons, rounded controls, generous spacing and visible keyboard focus. No scores, streaks, celebratory animation, judgmental copy, or required typing. Both exercises stay equally available. No History screen in this stage. The optional conversation opens directly from Home without a questionnaire.

Shared sticky Pause/Crisis Support header remains usable during requests/failures. Every active exercise shows Exit; leaving is immediate and never requires feedback. Screen headings receive focus after navigation, step headings after Continue/Back. Targets: at least 44×44 CSS pixels, readable contrast, narrow-width reflow, reduced motion and text alternatives. Grounding circles are 56×56 with 12px gaps at 390px; selected state uses both a checkmark and color plus aria-pressed. These are implemented targets with limited rendered checks, not full accessibility certification. At smaller widths/larger fonts content may scroll; safety remains sticky and no content is clipped intentionally.

## Daily mood and home

First opening per local calendar day shows the existing dismissible native dialog with Calm/Okay/Anxious/Overwhelmed, Skip, Close, Escape, and its own visible Crisis Support inside the modal scope. Dismissal is immediate locally and keyed by date; network failure cannot reopen the prompt. Storage denial reduces guarantees to this visit. Mood is optional self-report, not an assessment or diagnosis. Opening support dismisses the prompt as Skip.

Home: “Take a moment.” Top card “Stop to chat — Ai assistant conversation,” followed by directly accessible cards “Paced Breathing — About 60 seconds” and “5-4-3-2-1 Grounding — About 60–75 seconds.” Breathing icon is unchanged; Grounding uses a simple eye/awareness outline with the full text label. The card order stays stable. No automatic exercise selection, distress inference, or navigation restrictions.

## Paced Breathing — hold to run

Opening shows a static circle, “Press and hold to begin.”, disabled Finish, Exit and persistent Crisis Support. No session/timer starts until a hold or accessible Start. Hold continuously through inhale (4s expansion) and exhale (6s contraction). Release freezes the current phase/countdown/progress and says “Paused — press and hold to continue.” Rehold resumes accumulated active time and the same SQLite session. There is no inhale/exhale correctness feedback and no Hold/Tap/Observe selector.

The planned portion is six cycles,60 active seconds. A neutral planned-complete notice appears afterward; phases continue optionally until Finish or Exit. Finish is prominent and records completed even if chosen early; it means the person finished, not that six cycles were completed. Exit/support record exited. No mandatory repeats, scoring, auto-completion or model-controlled instruction. Planned duration, active duration, optional continuation, wall duration and setup remain distinguishable.

The native Start without holding/Pause button accommodates sustained-press difficulty; Space/Enter can hold the circle or activate the alternative. Pointer capture/cancel, lost focus, window blur and hidden-page pause prevent unattended timing. Page departure attempts an exited save. A static visual under device/manual reduced motion preserves textual cues. A stable210px circle hit target remains dominant with large Finish/44px alternative and visible focus. New summaries measure application active time, not actual breathing or clinical benefit. No raw interaction events are saved. See [contracts](design-pipeline.md) and [evidence](evidence/part-3-2-hold-breathing/index.md).

## 5-4-3-2-1 Sensory Grounding

| Step | Sense | Exact instruction | Circles | Intended time |
| --- | --- | --- | --- | --- |
|1|Sight|Notice 5 things you can see.|5|20 seconds|
|2|Touch|Notice 4 things you can feel.|4|15 seconds|
|3|Hearing|Notice 3 things you can hear.|3|15 seconds|
|4|Smell|Notice 2 things you can smell.|2|10 seconds|
|5|Taste|Notice 1 thing you can taste.|1|10 seconds|

Show only the current instruction, “Step N of 5 · Sense,” five discrete step segments, optional tap circles, and “N of M noticed.” Each circle is a native button labeled “Mark item N noticed,” with aria-pressed=false/true. A tap fills it with a visible checkmark; tapping again undoes it. Counts describe taps only, not emotional state, skill quality, or clinical improvement.

Continue is always enabled, including zero circles. Its nearby copy says “You can skip any step. Continue when you’re ready.” Continuing with partial/zero circles is a skip without penalty, validation message, forced reflection, or extra confirmation. Back appears on steps 2–5 and preserves all earlier selections within this exercise. Fifth Continue reaches the existing completion view. No automatic advance/countdown/deadline. Exit and Crisis Support are available at each step; both end the session as exited. Returning from support goes home, never resumes automatically. Restarting Grounding resets tap state. No descriptions, sense details or reasons are requested/stored.

Timing assumption:20+15+15+10+10=**70 seconds**, matching the home range of60–75 seconds. This is an intended walkthrough budget including ordinary reading/tapping/transitions, not an enforced clock. Actual duration runs from the first mounted instruction to final Continue/Exit, including application delays and voluntary reflection/backtracking. Entry/setup is measured separately. User-chosen pauses, accessibility needs or backtracking may extend actual duration beyond 90 seconds; never force completion or exit. [Verification](verification.md) records the actual fictional walkthrough separately from this estimate. No model/save wait contributes to exercise progression.

## Completion, model boundary, and persistence

Completion remains “Exercise complete.” Optional Helpful/Not Helpful/Skip and Return Home; no feedback required after Exit. Helpful/Not Helpful save activity then request one short response; Skip sends no generation request. Home/Crisis remain enabled during loading/failure. Model source labels distinguish mock/live; static fallback is explicitly not generated. Only exact reviewed neutral text is accepted by backend code and rendered as escaped text. No model-generated instructions, step changes, extra disclosures, diagnosis, therapeutic advice, tools/actions, navigation, support resources, or database writes.

Grounding identifier is grounding_54321; fixed button message includes “5-4-3-2-1 Grounding.” Fixed exercise/feedback plus optional scoped mood and at most three recent supported exercise summaries reach generation. Application/session IDs, timestamps/durations and circle taps do not. Existing deterministic mock and OpenRouter live configuration are preserved; the Grounding-only revision was tested using mock mode; the later recommendation refinement has separate live evidence in verification.md.

The earlier schema 4 added Grounding to the existing session/conversation exercise constraints and sets its planned_duration_seconds=70; breathing/historical STOP retain 60. A transactional migration preserves every old session, conversation, message, ID and relationship. Actual completed/exited states, elapsed time, separate setup and optional feedback remain scoped by the local application UUID. Historical stop values remain readable/valid for compatibility but no STOP card/component is active. Circles are transient Vue state, never persisted. No unrelated tables or fixture reseeding. The recommendation refinement below describes the current schema 5 changes.

Frontend owns views/fixed steps/taps/navigation/timing; FastAPI owns validation, provider boundary and writes; only backend opens data/app.sqlite3. Backend/.env remains private/ignored; examples contain no keys. See API/model ownership and duplicate/failure contracts in design-pipeline.md. Local UUID scope is not authentication. No durable offline outbox, retention UI, RAG/history or Figma work is added here.

## Crisis information and limits

Existing bundled U.S./territory-specific support information remains independent of model/backend requests and accessible from every relevant state, including inside the mood dialog. Geographic limitations, compatibility/network needs for external contact, and no-monitoring/coursework language remain unchanged. This revision does not launch calls/text/chat or alter resource content; earlier resource-verification dates/sources remain in historical design and verification notes. Fixed feedback accepts no free text; no distress classifier, inferred diagnosis, or monitoring is implied.

## Revised rationale and evidence

R1:70-second intended path, actual/setup measured separately. R3:Exit and optional skip at every step. R4:manual Continue/Back/undo with no forced completion. D2:one current sensory instruction. D3:tap-only, optional actions, no emotional disclosure. D6:exact neutral copy and observable progress without judgment. This design iteration is documented evidence of a revised approach in AI-assisted development: the developer supplied the replacement and exact instructions; the coding agent implemented/migrated/tested it. Testing uses fictional activity only; taps cannot establish therapeutic benefit.


## Historical Help Me Choose — refinement of Part 3.1

Superseded October26 by the direct conversation experience below; retained as design history.

The developer requested a more meaningful optional AI role without making AI a prerequisite. Add the top Home card and a simple branching/choice icon; preserve equally accessible direct exercise cards. The new question is “What would you like to focus on?” with three large buttons: Slowing down, Focusing on my surroundings, Not sure. No required typing. A brief note discloses use of any saved mood/recent activity.

After selection, show distinct loading, success or static fallback. A valid success shows one of the two supported names, one short reviewed neutral explanation, a mock/live source label, Start Suggested Exercise, Choose Other Exercise with its name, and Return Home. Buttons change navigation only after the person explicitly taps them. Loading/failure instead offers both manual exercise buttons and Home; Crisis Support stays in the shared header. Entering support cancels waiting and returns home afterward. No inferred distress, clinical condition, crisis decision, forced suggestion, or automatically started exercise.

Backend retrieves optional mood for the client’s local date and at most three recent completed/exited supported sessions for the local application identity. It sends only mood enum and type/status/feedback summaries, not IDs/dates/times/durations, free text, observation circles, or complete history. Mood is self-report; use history only as activity context, never proof of emotional state or clinical benefit. Completion feedback now uses the same context. Helpful may acknowledge neutrally; Not Helpful may name the other existing exercise in a reviewed sentence. Neither changes the skill’s fixed steps/timing or requires disclosure.

Schema 5 reuses conversations/messages: a kind discriminator, optional focus and context snapshot, and nullable session/exercise/feedback only for recommendations. Existing feedback relationships and records are preserved. Store fixed user selection, actual accepted structured recommendation/reason, mock/live mode and success/failure; failed generation has no invented assistant. Enforce duplicate UUIDs/scope and suppress late responses after leaving. A new visit is a new request opportunity, not an automatic retry.

The model chooses only a supported identifier and a matching reviewed neutral reason. This replaces the former single acknowledgment-only boundary with a bounded choice/catalog contract rather than unconstrained clinical advice. No claims of therapy/monitoring, new exercises, instructions or generated support content. Reasons remain intentionally limited; richer language would require a separate reviewed policy. The design tradeoff is a third Home card and optional latency/data use; direct access, plain labels, transparent context and immediate exits preserve control. See research mapping and verification for actual evidence, not proposed guarantees.


## Historical closed-loop Breathing refinement — October 22, 2026

Superseded by the hold-to-run behavior above; retained to explain the design iteration.

The developer requested an observable interaction/feedback loop within the existing fixed breathing sequence. The circle is now a stable keyboard/pointer target; its decorative visual expands4s/contracts6s, six cycles, without interaction-gated progression. Hold (default) instructs press/hold on inhale and release on exhale; application code immediately displays Holding / Hold during inhale / Released / Release during exhale. Feedback sits below the main phase/countdown with no success/failure scoring or extra animation. Early release never restarts a cycle.

Tap Mode uses an ordinary button activation to indicate the current inhale/exhale phase; the cue resets at the next timed phase, so a stale tap does not count again. Native button Space/Enter activation works in Tap, and keydown/keyup implement Hold. Pointer capture plus release/cancel/blur cleanup avoids stuck input. Observe removes the interactive circle target and preserves visual/textual cues. Mode changes preserve elapsed timing. Reduced motion disables visual scaling, while text/countdown, a fixed hit target, visible focus, Exit/support and optional completion remain available.

A compact three-button mode group adds choice/reading; the circle is230px rather than276px to keep all controls readable at390×844. This is an intentional change to the earlier timed-only design. The circle remains dominant; feedback has a reserved line and no overlay. Button cues explicitly do not measure breathing. Saved summaries are optional phase observations, not physiological evidence; no raw events/scores/clinical inference or AI-generated interaction feedback. Old SQLite rows remain unchanged with NULL new fields. See current [API contract](design-pipeline.md) and [verification](verification.md).


## Direct conversation — October26 current design

The developer replaces predefined exercise-choice questionnaires with the existing conversational voice panel. Home uses the latest browser-requested labels **Stop to chat / Ai assistant conversation**, with a simple labeled speech-bubble icon, and opens **Talk to Pause** directly. Both fixed exercises remain equally available without AI. No focus buttons, generated recommendation card, suggestion-only loading states or model navigation controls remain. The voice panel has the existing microphone/status/Mute/End/playback/transcript controls, Return Home and independent sticky Crisis Support. No microphone/config/provider request on entry; use requires explicit microphone selection.

Existing voice models/personality instructions and lifecycle are preserved. Spoken suggestions remain optional and explain manual exercise selection; no navigation tool exists. Voice transcripts stay transient and are not saved. The developer confirmed existing voice plus post-exercise text feedback, with no new typed-chat composer. Shared feedback generation/storage/context remain; historical recommendation reads/schema remain but creation is removed. This trades fixed choices for conversational flexibility without promising stronger personalization or clinical effectiveness. A voice-only conversation has hearing/speech/hardware/network limitations; exercises and text feedback remain available, while a general typed conversation remains outside this increment. See [evidence](evidence/part-3-2-conversation/index.md).
