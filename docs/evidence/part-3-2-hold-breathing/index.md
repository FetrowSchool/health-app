# Hold-to-run Paced Breathing evidence — October 26, 2026

Fictional local review at390×844, normal saved backend configuration, zero provider calls. This changes only breathing interaction/timing/session summaries. The original Part3.1 and October22 previews remain historical.

- [Idle / no session started](01-idle-390x844.png)
- [Released / frozen exhale](02-paused-390x844.png)
- [Planned portion complete / optional continuation](03-planned-complete-390x844.png)
- [Reduced motion and keyboard focus](04-reduced-focus-390x844.png)
- [Explicit Finish / feedback skipped and saved](05-finished-saved-390x844.png)
- [Selected fictional database and preservation evidence](database-evidence.json)

Automated commands: `backend/.venv/bin/python -m unittest discover -s backend/tests -q` (93 passed); `cd frontend && npm test` (75 passed); `cd frontend && npm run build` (36 modules, passed). The9 focused backend checks and14 focused frontend checks are subsets, not additional totals. Existing voice/AI/Grounding checks are included and use mocks. No paid/live model behavior is claimed. Known non-failing Starlette TestClient deprecation warning persists.

Runtime preservation inspection uses Python sqlite3 read-only connections and a pre-change SQLite backup outside Git. Every original value is compared by projecting the original columns, including composite-key mood rows. Only schema metadata changes6→7; new nullable timing columns preserve historical values. No app identity, message contents or secrets are exported. New selected session IDs are fictional verification records only. Timing is application active time, not respiration evidence. See [verification notes](../../verification.md) for observed results and limits.

Final rebuilt wording uses “Release or select Pause to pause.” so the hands-free alternative receives an accurate cue. Final75 frontend tests and36-module production build passed (16.26s build after tooling loaded). The backend93-test result remains current; no backend edits followed it. Manual browser Tab away from the running Start/Pause control paused immediately; Enter hold resumed. With reduced motion On, the running visual computed transform none. Early Finish b5e9d0e5-ae14-4fa0-b740-78f57bea48ab saved completed at0.840 active seconds/7.062 wall seconds,0 cycles,0 continuation; Skip saved with no generation. Scoped GET matched SQLite after equivalent Z/+00:00 timestamp normalization. Final counts64 sessions/11 moods/35 conversations/66 messages: four intentional fictional session rows, no new conversation/message records.

Service state: normal saved live configuration restored on FastAPI8000 (PID47165), preview5173 (PID38123, existing built-output server), separate diagnostic8001 preserved. Health200/database ready/model configured; proxy voice config200/configured60. These read-only checks do not establish new live-model availability. report.md/.env/protected Grounding/AI/voice hashes all unchanged. Browser viewport reset after captures; ready screen may be left open without starting a session.

Follow-up UI copy removal: [current screen without the selected sentence](06-copy-removed.png). Earlier five captures preserve the original review state. Production build and separate idle-browser check passed; the user’s paused session was retained.
