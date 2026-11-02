# Assignment 3.3 submission checklist — Pause

November 2, 2026 · published branch `main`. The application commit below is verified on GitHub; unfinished recording/accessibility/behavior items remain explicit.

| Submission item | Value/status |
| --- | --- |
| Repository URL | [FetrowSchool/health-app](https://github.com/FetrowSchool/health-app), taken from the configured origin. Remote visibility/access was not rechecked in this documentation run. |
| Application commit cited in report | [9b4e53081576852e8ff4d62da8aca1d48fc36d7c](https://github.com/FetrowSchool/health-app/commit/9b4e53081576852e8ff4d62da8aca1d48fc36d7c). The following report/documentation commit intentionally retains this reference rather than attempting to cite itself. |
| Application demonstration recording | An owner-supplied demonstration URL appears in [report.md](../report.md). [Recording outline](demo/application-demo.md); recording playback and audience access have not been verified here. |
| Process screencast recording | **[TO FILL with the actual tested viewer link]**. [Failure/code walkthrough outline](demo/process-screencast.md); no completed recording/link verified. |
| Fictional scenario evidence | [Scenario index](evaluation/scenarios.md), [original evaluation matrix](part-3-evaluation.md). Unexecuted/unscored live cases retain that status. |
| Three explicit behavior checks | [Behavior checks](evaluation/behavior-checks.md): BC1 passes tested conditions; BC2 partial; BC3 fails voice unsupported-content criteria. |
| Full verification evidence | [Latest submission checks](evidence/part-3-3-submission/index.md), [clean/browser/database evidence](evidence/part-3-3-clean/index.md), [verification chronology](verification.md). |
| AI-use disclosure | [AI-USE.md](../AI-USE.md), [curated redacted development log](ai-development-log.md). |
| Current design/research/flow | [Design](design.md), [instructor-study mapping](research-decisions.md), [user flow](user-flow.md), [implementation contracts](design-pipeline.md). |

## Before submitting

- [x] Reviewed and committed the intended source/tests/docs/screenshots from the [pre-publication untracked inventory](evidence/part-3-3-submission/untracked-evidence.json). No configured credentials or runtime databases/dependencies/build output were included.
- [x] The application commit includes History and all new documentation/evidence; these files are now available through the published main branch.
- [x] Confirmed the application commit on remote main and set the report reference to that existing hash. The metadata commit does not replace that reference with its own hash.
- [ ] Record both videos, use fictional inputs, add/review captions, verify playback and test the actual links with the intended audience's access. Do not paste placeholder URLs into the submission as completed links.
- [ ] Check the instructor's actual rubric/duration/access requirements and acknowledge unresolved behavior/evidence gaps. Do not describe a mock screenshot as live or a configured model as used.
- [ ] Recheck evidence/source labels and startup instructions for the submitted commit. Keep useful STOP/Help Me Choose history clearly marked historical.

## Remaining limitations to disclose

- Voice transcripts still accept unsupported-exercise/professional-therapy claims. Fixed exercise logic/actions are isolated and text feedback uses a reviewed catalog, but this is not universal spoken-content rejection.
- GPT-Live transport/output/automatic closure was observed once; scripted conversational quality, live refusal/interruption, real manual Mute/End and live delegated `gpt-6-luna` reasoning remain unverified/unscored.
- Full screen-reader speech/device testing and actual 200% browser zoom remain pending; limited keyboard/mobile/reduced-motion/AX checks are not full accessibility certification.
- No durable offline write retry queue; abrupt closure can leave started sessions. Local UUID scope is not authentication or account recovery. History shows 20 recent records per section without pagination/deletion UI; voice is not persisted.
- Model-proposed SQL RAG and Figma capture were not implemented/performed; fixed SQL History is not RAG. Confirm the course milestone expectations without claiming these capabilities exist.
- Original iCloud-backed files can delay cold startup; the credential-free temporary clean setup worked. The pre-publication untracked-file gap was resolved by the application commit.

The app supports a supervised local demonstration, with these limits. This checklist does not certify all safety checks, complete recordings or publication. Only the commit-hash field in report.md was changed by the publication step; the owner's report prose and demonstration URL were preserved.
