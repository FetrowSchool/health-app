# AI use in Pause

Prepared November 2, 2026 for Assignment 3.3. This disclosure distinguishes development assistance, runtime model configuration and observed live use. Exact versions are supplied only where the project records them. It does not include private chats, credentials, raw voice recordings or third-party project content.

## Tools and models used

| Tool/model | Identifier/version available | Role | Evidence and limits |
| --- | --- | --- | --- |
| **Codex coding agent** | Codex desktop/local coding workflow. Exact app build and underlying coding-model identifier were not recorded in the repository. | Generated and revised Vue/FastAPI/SQLite code, tests, static mockups, documentation and prompts; inspected failures, ran mocked checks/builds and helped collect redacted evidence. | [Curated development log](docs/ai-development-log.md), source/tests and [verification chronology](docs/verification.md). Do not infer a coding-model version from the application's runtime model settings or a plugin package version. |
| **ChatGPT** | ChatGPT; exact selected model/version not recorded. | Planning, design discussion, development instructions and staged prompts supplied through the developer's iterative workflow. | The log summarizes the resulting instructions and decisions, rather than fabricating verbatim ChatGPT transcripts. R1–R4/D1–D6 come from the instructor-provided study summary, not original ChatGPT research or evidence of clinical effectiveness. |
| **OpenRouter text-model service** | Requested identifier `nvidia/nemotron-3-ultra-550b-a55b:free`. This is a model identifier, not an independently verified weights/build version. | Optional post-exercise text responses; earlier Help Me Choose recommendations before that interface was retired. FastAPI calls the provider; keys are never in Vue. | **Live requests confirmed historically**, including accepted saved feedback and earlier recommendations. [October 19 live evidence](docs/evidence/part-3-2-final/index.md), [Grounding investigation](docs/verification.md#october-19-2026--investigated-demofallback-output-after-grounding). Those calls were not repeated for submission documentation. The current text path accepts a reviewed response catalog, not unrestricted typed chat. |
| **OpenAI GPT-Live-1** | API model `gpt-live-1`; configured output voice `gleam`. No finer model snapshot/version recorded. | Native WebRTC real-time spoken conversation, transient input/output transcript display, optional spoken suggestions. Application code owns exercises, navigation and support. | **One successful live connection confirmed November 2**: one approved POST, provider 201/1151ms, Active and assistant output, then confirmed automatic closure. [Sanitized result](docs/evidence/part-3-3-clean/approved-live-outcome.json). The three fictional semantic turns were not completed/scored; this does not establish universal prompt adherence, audible-interruption quality or content safety. |

### Configured delegation is not confirmed model use

`delegation.responses.model` is **`gpt-6-luna`** (GPT-6 Luna) in [backend/app/voice_session.json](backend/app/voice_session.json), with separate delegated instructions. The saved successful voice-test metadata names that configuration, but contains no observed delegated Responses result or usage event establishing that Luna actually ran. It is therefore **configured / live execution not verified**, and is not counted as a confirmed-used runtime model above. Mocked outgoing-payload tests establish configuration delivery, not live delegated reasoning. No claim is made that configured web-search tools executed.

The runtime prompt locations are the JSON's `instructions` and `delegation.responses.instructions`. [prompts/01](prompts/01-pause-voice-assistant-system.txt) and [prompts/02](prompts/02-pause-voice-assistant-system.txt) are preserved staged drafts; `backend/app/voice_prompts.py` is historical, not the current runtime source. Merely editing a draft did not activate it; see the [prompt-delivery finding](docs/evidence/part-3-2-voice/prompt-delivery.json).

## Mock tests, live evidence and developer decisions

Most checks use the deterministic application `MockProvider` or injected HTTP/browser mocks. A Demo label, canned voice transcript or passing mock test is **not** live model use. [Full submission checks](docs/evidence/part-3-3-submission/index.md) state which tests were freshly rerun; earlier browser/live checks retain their original dates.

The developer supplied scope, exercise instructions, interaction revisions and interface wording; the agent implemented and checked those directions. Design changed through review: STOP was replaced with Grounding, the questionnaire was replaced with direct conversation, and Breathing was revised to hold-to-run/release-to-pause. These are development decisions, not clinical findings. The [development log](docs/ai-development-log.md) connects instruction summaries to concrete files, observed results and subsequent decisions.

AI output was not accepted solely because it compiled or sounded plausible. Tests exercise timing, persistence, stale requests, validation and failures. The evaluation still records **failed voice transcript rejection of unsupported exercise/therapy claims**, unscored live refusal/interruption, and incomplete screen-reader/zoom coverage. [Behavior checks](docs/evaluation/behavior-checks.md). A successful connection does not resolve those gaps.

## Data, privacy and unimplemented claims

- Text feedback stores fixed user selections and actual accepted assistant replies with source/status and related record IDs. Failed model calls do not fabricate assistant messages.
- Voice audio/transcripts remain transient in the application and are not written to its SQLite database. This is not a claim about provider retention. Incidental non-script speech was excluded from exported live evidence; only sanitized transport/closure metadata was retained.
- Credentials remain in ignored backend/.env and are absent from disclosure/evidence. Only fictional test records and redacted observations are included. Previous Expedia Lite code was inspected as a pattern reference; its private data/content is not reproduced here.
- No Figma capture, image-generation model use or model-proposed SQL RAG implementation is claimed. History/context retrieval uses application-owned fixed SQL; it is not the proposed two-model-call SQL RAG workflow.

See the [submission checklist](docs/submission-checklist.md) for actual evidence links, recording placeholders and remaining work. No new live call was made while preparing this disclosure.
