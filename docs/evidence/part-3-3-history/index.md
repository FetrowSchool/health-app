# Part3.3 History and recent-exercise evidence — November1, 2026

Fictional browser review at390×844 on isolated frontend5190/backend8090 and a temporary database. The normal database was inspected read-only; no real message content is exported. No model calls were made.

- [Empty history](01-empty-390x844.png)
- [Home: correct recently completed exercise, all direct cards](02-home-recent-390x844.png)
- [Sessions: unfinished, exited, completed and distinct active/total timing](03-exercises-390x844.png)
- [Recent conversations and generic previews](04-conversations-390x844.png)
- [Saved user/assistant messages](05-messages-390x844.png)
- [Failed generation: only the actual saved user message](06-failed-record-390x844.png)
- [Conversation retrieval failure](07-detail-error-390x844.png)
- [History retrieval failure](08-history-error-390x844.png)
- [Loading with immediate navigation](09-loading-390x844.png)
- [Actual isolated backend stopped](10-backend-offline-390x844.png)
- [Rendered fictional conversation/message IDs and content](rendered-conversation.json)
- [SQLite/API/UI comparison and scoped API results](database-api-evidence.json)
- [Original data and protected-file preservation](preservation.json)

Passed:92 backend tests,79 frontend tests,37-module production build. The6 focused backend and9 focused frontend History checks are subsets, not extra totals. Repeat from project root: `backend/.venv/bin/python -m unittest discover -s backend/tests -q`, `npm --prefix frontend test`, `npm --prefix frontend run build`. Tests create temporary fictional databases, validate identity/limits/errors, reject writes on the read-only connection, preserve old rows after reads/restart and never call a real model provider. Known non-failing Starlette TestClient deprecation warning remains.

Manual browser method: new isolated origin → Skip fictional daily prompt → empty History → seed owned fictional completed/exited/unfinished/historical records plus another identity → reload → Home recent label → History → open a saved conversation. Compare its UUID and both message UUIDs/roles/text/UTC times across a Python sqlite3 read-only query, scoped GET and DOM data attributes. All match after equivalent Z/+00:00 normalization. A newer exited/started session never replaces the completed Grounding label; other-owner rows are absent. Both direct skills/Exits remain usable while the isolated backend is stopped. Missing saves are honestly unsaved. No crisis contact links operated.

History list/detail read failures were injected only in the temporary server. A2-second delayed request allowed immediate Return Home; late response did not reopen History or move focus. The isolated backend was actually stopped for offline History/support checks, then restored for the final comparison. Invalid UUID422, wrong scope404 and excessive limit422 were also verified through actual read endpoints. Normal proxy5173→8000 returned200 with empty scoped history for a fresh unknown identity. No writes occurred on any History read. No raw message/mood text appears in list previews; opened messages are escaped saved content, not generated placeholders.

Mobile observations: Home, empty, selected conversation and failure states fit390×844; lists intentionally scroll vertically with390px scroll width. Sticky Crisis Support and Return Home remain usable. Return Home56px, keyboard3px focus; native conversation cards are large labeled targets. Full screen-reader/zoom/touch-device testing remains pending. The rendered example shows66.147 active versus95.881 wall seconds as1m6.1s /1m35.9s, using0.1s rounding.

All original normal-app records preserved:73 sessions,13 moods,36 conversations,67 messages and schema metadata7; FK check empty. A concurrent daily check-in through the existing normal-app endpoint brought the final mood count to14; no original row changed and the new row was retained. It is not the fixture identity; its value/identity are not exported. report.md/.env/schema/exercises/voice/provider/session/mood/crisis protected hashes unchanged. Part-2 resumed at existing48f912d from published main without a new commit; no report edits/commits/pushes/install. Test fixture code/data live outside the repository under the private History snapshot; the tests above provide repeatable fixtures.

Limits:20 items per section (API allows1–50), no pagination/deletion/account recovery, local identity is not authentication, no voice audio/transcript persistence, no new live voice/model check. History is a read snapshot; reopen to refresh pending exchanges. Existing offline-write/abrupt-close limits remain. This stage does not implement model-proposed SQL RAG or complete the later full evaluation/demonstration. Current implementation, contracts and results are in [README](../../../README.md), [design pipeline](../../design-pipeline.md) and [verification](../../verification.md).
