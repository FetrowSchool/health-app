# Part 3.2 final submission evidence

October 19, 2026 · branch `part-2` · fictional scenarios only. No new live-model calls were made during final verification. These are screenshots of the working application, not the earlier static design gallery.

## Browser captures

All primary captures use a 390 × 844 viewport. The two live captures are unchanged copies from the earlier verified October 19 Help Me Choose run; their provenance and database IDs are below. All other captures were made during final verification on an isolated local origin, with injected mock providers or the backend stopped. No contact links were activated.

| Required view | Evidence | Source / observation |
| --- | --- | --- |
| Daily mood popup | [01 — mood](01-mood-390x844.jpg) | Before fictional Okay selection. Skip, close and an operable in-dialog Crisis Support control remain visible. |
| Home | [13 — Home, Simplify removed](13-home-without-simplify-390x844.jpg) | Latest developer-requested layout; all three cards and persistent support fit without scrolling. [Earlier capture](02-home-390x844.jpg) retained as history. |
| Help Me Choose recommendation | [03 — live recommendation](03-recommendation-live-390x844.jpg) | Earlier actual OpenRouter success; Model suggestion, supported Grounding, explicit Start/Other/Home. Conversation c0b7dc1a-6dbe-4653-b131-8b1df0a7481c. |
| Paced Breathing in progress | [04 — Breathing](04-breathing-390x844.jpg) | Current corrected spacing, Cycle 1/6, inhale countdown, Exit/support/reduced motion. |
| Grounding in progress | [05 — Grounding](05-grounding-390x844.jpg) | Current corrected spacing, five optional circles, Continue/Exit/support. |
| Completion with live feedback | [06 — live completion](06-completion-live-390x844.jpg) | Earlier actual OpenRouter success; Model response and saved feedback. Conversation 428a0c07-112a-4964-afe5-2940fb3705cb. |
| Crisis Support | [07 — backend offline](07-crisis-backend-offline-390x844.jpg) | Backend actually stopped; information and resource links still render locally. Lower content is vertically scrollable; see full-page capture. |
| Model failure | [08 — provider failure](08-provider-failure-390x844.jpg) | Injected provider_error; explicit Static fallback · not a model suggestion. Home/support/manual choices remain. |

Additional evidence: [09 — loading](09-loading-390x844.jpg), [10 — complete scrollable crisis page](10-crisis-full-page.jpg), [11 — Exit despite failed writes](11-exit-save-failure-390x844.jpg), [12 — mock recommendation](12-recommendation-mock-390x844.jpg).

The live originals are [recommendation](../part-3-2-choice/recommendation-live-390x844.jpg) and [feedback](../part-3-2-choice/contextual-feedback-live-390x844.jpg). They were inspected again and matched to SQLite and scoped GET responses without invoking generation. Provider: OpenRouter; requested model: `nvidia/nemotron-3-ultra-550b-a55b:free`. Historical HTTP traces and timings are in [verification](../../verification.md). Mock results have Demo labels; provider failures have no fabricated assistant message.

## SQLite and persistence

[Selected database evidence](database-evidence.json) contains five known fictional sessions, one fictional Okay check-in, four conversations and seven ordered messages. Application identities are omitted. It includes completed Breathing and Grounding, exits from both skills, feedback fields, live/mock source/status, safe failure code, message IDs/roles/order, and session→conversation→message relationships. Failed conversation has only a user message. Recommendations intentionally have no session FK. Feedback is stored on sessions, not in a separate feedback table.

Inspection used Python sqlite3 with `mode=ro`, parameterized selection of known fictional IDs and scoped GET requests; the actual database was not copied into evidence. Four GET comparisons matched source/status and ordered message IDs/content. Foreign-key check returned no violations. Full row-value snapshots before and after an actual backend shutdown/restart matched: 45 sessions, 31 conversations, 58 messages, 3 moods at that checkpoint. Later deliberate checks added records, so those checkpoint counts are not final totals. Existing unrelated content was excluded from this export.

[Read-only inspection SQL](inspection.sql) documents the queries. Run against local `data/app.sqlite3`; it is intentionally not a fixture/seeding script. Runtime data and credentials remain ignored.

## Timing and evidence limits

| Exercise | Intended | Observed guided duration | Separate entry/setup | Saved session |
| --- | --- | --- | --- | --- |
| Breathing | 6 × (4s inhale + 6s exhale) = 60s | 60.014s | 0.001s | 8155e4d3-9722-42b2-9900-a0ad278e6d44 |
| Grounding | 20 + 15 + 15 + 10 + 10 = 70s | 71.863s | 0.002s | c734adb7-c728-4436-93e4-e2bcb25917ec |

Grounding duration is a fictional manual walkthrough including observation/tool overhead and voluntary pauses, not a forced timer or a usability study. Optional taps were demonstrated; unmarked items never blocked Continue. User-chosen pauses can extend duration beyond 90 seconds. No clinical benefit is established.

Automated final result: 47 backend + 29 frontend = 76 passing tests; production build passed. Timeout/provider/storage failure tests use mocks. No new live availability claim is made. Full screen-reader/zoom/device testing, durable offline write retry and abrupt-close recovery remain limitations; dedicated History is deferred to Part 3.3. The instructor's later model-proposed SQL RAG workflow is not implemented by the current fixed-SQL context lookup. Confirm its submission milestone against the assignment rubric.
