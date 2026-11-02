# Submission documentation and final automated checks

November 2, 2026 · branch `part-2` · inspection base `48f912d1936142e230ae427f8592c616a6b7c6bf`. This is not a final submission commit. No functionality, credentials, runtime database, report.md, commit or push was changed by this organization task.

## Submission documents

- [Checklist](../../submission-checklist.md): repository URL from origin; final hash and actual recording links remain placeholders.
- [AI-use disclosure](../../../AI-USE.md): Codex/ChatGPT roles, historical live OpenRouter and confirmed GPT-Live transport; delegated gpt-6-luna configured only, not verified as executed.
- [Curated redacted development log](../../ai-development-log.md): instruction summary → code/design change → actual evidence → decision, including failed/revised approaches.
- [Application demo outline](../../demo/application-demo.md), [process screencast](../../demo/process-screencast.md): preparation only. Neither recording nor a viewing URL is claimed to exist.

## Fresh automated results

Existing credential-free validation checkout was reused, with 85 production/test/dependency files compared byte-for-byte to the original current tree. No source synchronization was needed and no dependencies were installed. [Source comparison](test-source.json). This is a new test/build run, **not** another fresh installation or live-model test.

| Check | Exact command from validation copy | Actual result |
| --- | --- | --- |
| Backend | `backend/.venv/bin/python -m unittest discover -s backend/tests -v` | 95 passed,1.677s; all provider paths mocked. |
| Frontend | From frontend: `npm test` | 85 passed,0 failed / 0 skipped,103.9285ms; browser/media/provider mocks. |
| Build | From frontend: `npm run build` | 37 modules, success130ms. |

**180 distinct tests passed.** [Machine-readable IDs/results](automated-results.json), [backend output](backend-tests.txt), [frontend output](frontend-tests.txt), [build output](production-build.txt). Passing regression tests that observe unsafe voice transcript acceptance do not mean the corresponding product criterion passed. No new model/provider call, browser exercise, database scenario or API connectivity check was executed in this documentation increment.

## Review, links and tracking

Reviewed README, AGENTS, current design/research/flow/contracts, verification/evaluation/demo materials and AI-USE. Current behavior is schema7/hold-to-run Breathing/Grounding/direct voice/post-exercise text/History/recent label. Earlier STOP, Help Me Choose, automatic-completion/three-mode Breathing, old schema and deferral descriptions are explicitly historical. Useful logs/artifacts remain intact. No typed-chat composer, ordering/reset preference, RAG or Figma capture is invented.

Eleven separate-project Expedia Lite hyperlinks were non-portable to a standalone checkout. They are now unlinked historical file descriptions; no private previous-project contents or made-up public URLs were added. [Repository-wide link audit](link-audit.json) covers relative Markdown file links and anchors, including read-only inspection of report.md; external HTTP availability is not inferred from a relative-link check.

Final audit: 28 Markdown documents, 473 relative links and 15 heading anchors; zero missing files, broken anchors or non-portable relative targets. All requested documentation files/directories are present. Inventory: 104 untracked files, including 83 evidence files, 12 Markdown documents and 13 implementation/test files (categories can overlap).

[Untracked evidence/source inventory](untracked-evidence.json) lists current untracked files and groups evidence, documents and implementation/tests. None was staged automatically. Intended new History/source/tests/evidence must be reviewed and included in a later authorized commit; files left untracked will not arrive in a clone. No .env/database/dependency/build artifacts are intended submission files.

[Preservation/check results](preservation.json) compare the original protected source/tests/dependencies/report/env against the private pre-task snapshot without exporting secret values/hashes. App services/data were not operated or modified in this stage. Test/build outputs are only the credential-free validation copy's outputs.

All 87 protected files were unchanged. The 28 changed/new deliverable text files checked contained no configured credential values, merge markers or unclosed Markdown fences. Scoped tracked-document whitespace checks passed. The saved environment, runtime database, dependencies and build directories remain ignored by Git.

## Existing evidence and remaining gates

- [Scenarios](../../evaluation/scenarios.md), [behavior checks](../../evaluation/behavior-checks.md), [clean setup/browser/SQLite evidence](../part-3-3-clean/index.md) and [verification chronology](../../verification.md) retain their dates and method boundaries.
- [One approved live result](../part-3-3-clean/approved-live-outcome.json) confirms GPT-Live connection/output/automatic closure, not scored fictional conversational turns, manual live media controls or delegated Luna reasoning. No new paid call was made.
- Voice unsupported-content/therapy transcript rejection still fails; BC2 semantic refusal remains unscored; full screen-reader/zoom/device testing pending. Offline-write/abrupt-close/local-identity/20-row/retention and unimplemented model-proposed SQL RAG limits remain.
- Final commit/publication and both actual recordings/captions/tested audience links remain manual/approval-dependent submission steps. This organized evidence supports review, not an unconditional all-requirements-complete claim.
