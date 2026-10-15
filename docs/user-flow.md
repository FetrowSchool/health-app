# Initial user flow

Five screen types are shown; four STOP states belong to one screen type. Crisis information is an independently accessible auxiliary route. Saved-history review is reserved for Part 3.3 and is not in this diagram. See [design](design.md) for exact behavior and [research decisions](research-decisions.md) for rationale.

```mermaid
flowchart TD
    Open[Open Pause] --> Day{Answered or skipped on current local date?}
    Day -->|Yes| Home[Home: both exercise cards]
    Day -->|No| Mood[Daily mood dialog over home]
    Mood -->|Calm / Okay / Anxious / Overwhelmed| Home
    Mood -->|Skip / close / Escape| Home
    Home -->|One tap| Breath[Paced Breathing: six 4s inhale / 6s exhale cycles]
    Home -->|One tap| S1[STOP 1: Stop]
    Home -->|Simplify view toggle| Home
    Breath -->|Six cycles complete| Done[Completion and optional feedback]
    Breath -->|Exit or background interruption| Home
    S1 -->|Next| S2[STOP 2: Take a Step Back]
    S2 -->|Next| S3[STOP 3: Observe]
    S3 -->|Next| S4[STOP 4: Proceed Mindfully]
    S2 -->|Back| S1
    S3 -->|Back| S2
    S4 -->|Back| S3
    S4 -->|Finish| Done
    S1 -->|Exit| Home
    S2 -->|Exit| Home
    S3 -->|Exit| Home
    S4 -->|Exit| Home
    Done -->|Helpful / Not Helpful / Skip| Feedback[Completion: feedback chosen; save separately]
    Feedback -->|Optional: Show a brief response| Response[Completion: pending / approved response / static fallback]
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
    Done -->|Crisis support| Crisis
    Feedback -->|Crisis support| Crisis
    Response -->|Crisis support, including model failure| Crisis
    Crisis -->|Return home: entered from mood / home / exercise| Home
    Crisis -->|Return to completion: entered from completion| Return[Restore previous completion state and feedback]
    Return --> Done
```

Feedback and response nodes are states of the same completion screen, not additional screens. Restoring completion preserves selected feedback and approved text; it does not automatically issue another model request. A saved return-state token determines the crisis route's return destination.

Every exercise Exit is immediate and records exited status if persistence is available. Crisis access marks an active exercise interrupted and never resumes it automatically. Opening crisis information from the mood dialog records a daily Skip. Crisis resources remain visible if any save/model request fails; no arrow waits for an AI response or successful database write. Daily dismissal uses browser-local date state first and SQLite later. Model failures use neutral static UI copy while home and crisis buttons stay enabled; they do not create a model-reply record. Feedback/model nodes describe the visible state, not guaranteed database persistence. A failed save is shown as unsaved; no arrow waits on a successful write. Stable card order remains default; any optional ordering changes neither available exercise nor navigation. Automatic breathing completion ends the planned sequence, not permission to remain or leave; Return home remains voluntary.
