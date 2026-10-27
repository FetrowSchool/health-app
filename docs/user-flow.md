# Current user flow — interactive skills

The original screen types plus direct AI conversation are shown; five Grounding states belong to one screen type. Crisis information is an independently accessible auxiliary route. Saved-history review is reserved for Part 3.3 and is not in this diagram. See [design](design.md) for exact behavior and [research decisions](research-decisions.md) for rationale.

```mermaid
flowchart TD
    Open[Open Pause] --> Day{Answered or skipped on current local date?}
    Day -->|Yes| Home[Home: both exercise cards]
    Day -->|No| Mood[Daily mood dialog over home]
    Mood -->|Calm / Okay / Anxious / Overwhelmed| Home
    Mood -->|Skip / close / Escape| Home
    Home -->|One tap| Breath[Paced Breathing: idle, hold or accessible Start]
    Home -->|One tap| S1[Grounding 1: Sight — 5 things]
    Home -->|Stop to chat| Chat[Talk to Pause: voice closed, no automatic request]
    Chat -->|Select microphone| Voice[Permission / Connecting / Active / Muted / Closing / Closed / Error]
    Voice -->|Interruption / Mute / End| Voice
    Voice -->|Return Home: clean up voice| Home
    Chat -->|Return Home| Home
    Chat -->|Crisis Support| Crisis
    Voice -->|Crisis Support including failures: clean up voice| Crisis
    Breath -->|First hold or accessible Start: create one session| Running[4s inhale / 6s exhale: active time]
    Running -->|Release / Pause / blur / hidden| Paused[Freeze current phase and progress]
    Paused -->|Hold or accessible Start: same session| Running
    Running -->|60 active seconds| Optional[Planned portion complete: optional continuation]
    Optional -->|Continue holding or accessible Start| Running
    Running -->|Finish| Done[Completion and optional feedback]
    Paused -->|Finish| Done
    Optional -->|Finish| Done
    Breath -->|Exit before starting: no record| Home
    Running -->|Exit: exited save| Home
    Paused -->|Exit: exited save| Home
    Optional -->|Exit: exited save| Home
    Running -->|Crisis Support: exited save| Crisis
    Paused -->|Crisis Support: exited save| Crisis
    Optional -->|Crisis Support: exited save| Crisis
    S1 -->|Continue — partial or zero taps allowed| S2[Grounding 2: Touch — 4 things]
    S2 -->|Continue — partial or zero taps allowed| S3[Grounding 3: Hearing — 3 things]
    S3 -->|Continue — partial or zero taps allowed| S4[Grounding 4: Smell — 2 things]
    S2 -->|Back| S1
    S3 -->|Back| S2
    S4 -->|Back| S3
    S4 -->|Continue| S5[Grounding 5: Taste — 1 thing]
    S5 -->|Back| S4
    S5 -->|Continue| Done
    S1 -->|Exit| Home
    S2 -->|Exit| Home
    S3 -->|Exit| Home
    S4 -->|Exit| Home
    S5 -->|Exit| Home
    Done -->|Helpful / Not Helpful| Feedback[Save feedback without blocking navigation]
    Feedback -->|Request optional response| Response[Completion: pending / approved response / static fallback]
    Done -->|Skip — no generation| FeedbackSkipped[Completion: skipped]
    FeedbackSkipped -->|Return home| Home
    Done -->|Return home: feedback skipped| Home
    Feedback -->|Return home| Home
    Response -->|Return home immediately| Home
    Mood -->|Crisis support: dismiss as Skip| Crisis[Static crisis-support information]
    Home -->|Crisis support| Crisis
    Breath -->|Crisis support: interrupt session| Crisis
    S1 -->|Crisis support: interrupt session| Crisis
    S2 -->|Crisis support: interrupt session| Crisis
    S3 -->|Crisis support: interrupt session| Crisis
    S4 -->|Crisis support: interrupt session| Crisis
    S5 -->|Crisis support: interrupt session| Crisis
    Done -->|Crisis support| Crisis
    Feedback -->|Crisis support| Crisis
    Response -->|Crisis support, including model failure| Crisis
    Crisis -->|Return home: entered from mood / home / exercise| Home
    Crisis -->|Return to completion: entered from completion| Return[Restore previous completion state and feedback]
    Return --> Done
```

Feedback and response nodes are states of the same completion screen, not additional screens. Restoring completion preserves selected feedback and approved text; it does not automatically issue another model request. A saved return-state token determines the crisis route's return destination.

Every exercise Exit is immediate and records exited status if persistence is available. Crisis access records an active exercise as exited and never resumes it automatically. Opening crisis information from the mood dialog records a daily Skip. Crisis resources remain visible if any save/model request fails; no arrow waits for an AI response or successful database write. Daily dismissal uses browser-local date state first and SQLite later. Model failures use neutral static UI copy while home and crisis buttons stay enabled; they do not create a model-reply record. Feedback/model nodes describe the visible state, not guaranteed database persistence. A failed save is shown as unsaved; no arrow waits on a successful write. Stable card order remains default; any optional ordering changes neither available exercise nor navigation. Breathing has no automatic completion:60 active seconds triggers a planned-complete notice, while Finish records completed and Exit records exited. Opening/ready Exit creates no record.

Grounding circles toggle noticed/unnoticed; Back retains all in-exercise taps and Continue never requires them. Fifth Continue completes; no step advances automatically.70-second intended pace, actual duration/setup saved separately, no90-second forced deadline. Historical STOP is absent from selection but saved rows remain; the [original flow](history/part-3-1-user-flow.md) is preserved.

Conversation is optional and never gates exercise access. The assistant may suggest a supported exercise conversationally, but the user returns Home and selects it manually. No AI navigation tool or focus questionnaire exists. Voice starts only after microphone selection, remains transient and ends through existing cleanup on departure. The existing post-exercise text feedback remains; there is no typed-chat composer in this increment. Historical recommendation records remain readable, while the old creation route is removed.

Breathing release/cancel/focus loss pauses active time without resetting progress or duplicating the session. Hidden-page pauses; page departure attempts an exited save. Finish may be early or after optional continuation. Planned60s, active, optional continuation, total wall time and setup are distinct; none measures actual respiration. Native Start/Pause and reduced motion remain available; all navigation remains independent of saving.
