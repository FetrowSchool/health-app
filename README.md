# Pause — Assignment 3.1

Pause is a local mental health skills **coursework prototype**, not a mental health support service. It does not diagnose, provide therapy, claim clinical effectiveness, or imply human monitoring. Testing uses fictional scenarios only.

## Current milestone and chosen direction

Research, design, documentation, and static previews only. No working application, installed dependencies, database, credentials, model integration, or verified running interface exists. The previously open starter guidelines are now described by the established Pause design reviewed in this milestone.

- Skills: paced breathing, six 4-second inhale / 6-second exhale cycles (60 seconds), and four sequential, manually advanced STOP steps (about 60 seconds at intended pace).
- Journey: optional once-per-local-day mood popup → home → either exercise → optional completion feedback → home. Skip, immediate Exit, and independent crisis information preserve control. Normal use requires no typing or account.
- Interface: one action at a time, light neutral colors, muted blue, large labeled controls, visible focus, generous spacing, and reduced motion. Simplify view is user-controlled, never inferred from distress.
- Personalization: minimal prior activity can label a recently used card. Stable order is the default; optional mood/activity ordering is documented as a changeable alternative, never an automatic exercise selection or restriction.
- AI: an optional short neutral completion response uses limited exercise/feedback context. Code owns instructions and timing. Future SQL-based RAG remains a separate assignment capability requiring a reviewed contract before implementation.
- Tradeoffs: daily prompts still add friction, persistent safety consumes space, and minimal tracking limits personalization. The research mapping explains alternatives and reasons.

## Review documents

- [Design specification](docs/design.md): five screens, timing, AI, data, personalization, safety, and unresolved questions.
- [Research-to-design mapping](docs/research-decisions.md): R1–R4 and D1–D6, feature choices, reasons, alternatives, and limitations.
- [User flow](docs/user-flow.md): Mermaid navigation, interruptions, and optional response states.
- [Five-screen mockup gallery](docs/mockups/index.html): static HTML/CSS design previews.
- [Verification record](docs/verification.md): actual source checks and remaining limitations.
- [Development instructions](AGENTS.md) and [current handoff](handoffs/current.md).

Open `docs/mockups/index.html` directly in a local browser by double-clicking it in Finder or using Open File. Keep `styles.css` beside it. No server, network, build, or installation is needed. Buttons are inert; these previews are not a usable support route. Browser rendering, focus behavior, and viewport fit still require visual review.

## Proposed architecture and folders

Vue/JavaScript presents views, state, deterministic timing, and API requests. FastAPI/Python owns validation, controllers, configuration, SQLite access, and provider calls. Only the backend opens `data/app.sqlite3`; resolve its path relative to the project, not the current shell directory. Environment variables are explicitly loaded from future `backend/.env`; add ignore rules before credentials or runtime data, and use safe placeholders in a future `backend/.env.example`. Keys never appear in Vue, responses, logs, prompts, or screenshots.

```text
frontend/src/       Future Vue components and API client
backend/app/        Future FastAPI routes, controllers, models, and configuration
data/               Future app.sqlite3; fictional fixtures kept separate
backend/data/       Earlier empty placeholder, preserved; not the runtime target
docs/               Specifications, research mapping, flow, verification, mockups
tests/              Future fictional automated checks
prompts/            Future curated instructions
handoffs/           Current state and next step
```

Existing Expedia Lite patterns are identified in the research mapping; no code was copied. No setup/run/test commands are claimed for an application that does not exist.

## Future implementation and assignment requirements

Part 3.2 will implement and verify the agreed accessible five-screen flow, static crisis route, deterministic exercises, SQLite persistence, and optional backend feedback. Resolve provider, approved response content, retention, and any required conversational scope before coding.

The baseline assignment also requires SQL-based RAG: FastAPI requests a retrieval query, validates a single read-only statement with table/field and current-profile/conversation restrictions, bounds query time/results/context, then supplies relevant records and reviewed content in a second model call. The model never connects to SQLite. Writes remain separate, parameterized backend operations. Count both provider calls; use finite timeouts and reject untrusted SQL beyond a superficial SELECT check. This is a later integration plan, not an implemented feature or a required wait during exercises/ordinary history browsing. Its exact milestone and relationship to short completion feedback remain open for instructor confirmation.

Part 3.3 retains the required saved conversation-history and session table/timeline review plan. Display message IDs/order/time and session duration/completed/exited status via FastAPI, compare with SQLite after refresh/restart, and never infer clinical improvement from activity. Failed requests create no fabricated replies; failed writes cannot look saved; retries must not duplicate records. Configure and inspect services only in a later authorized implementation task. Figma/MCP capture and Vue revision are later tasks; static mockups are not editable Figma captures.

R1–R4 and D1–D6 are attributed to the instructor-provided Assignment 3 study summary; no external study citations or clinical-effectiveness claims are made. The initial crisis-information route will display U.S.-specific 988 details, explicitly limited to the United States and its territories; official resource sources and the October 15, 2026 check are recorded in the design and verification notes. Rendered mobile mockup review remains pending because the preview browser blocks local file URLs. Confirm course-specific bibliography formatting if required. Wait for the developer's review; no automatic commits or implementation.
