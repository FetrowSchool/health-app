# Closed-loop Breathing evidence — October 22, 2026

Branch part-2. Fictional scenarios only; all provider checks in this increment used deterministic mocks. No new live-model calls. These captures show the working application at390×844, not the older static mockups.

- [Hold with both save notices](hold-save-notices-390x844.jpg): default mode, instruction, optional-input limitation, all controls fit.
- [Keyboard focus on circle](hold-390x844.jpg): Space activation; visible3px outline on the fixed230px target.
- [Released during exhale](released-390x844.jpg): neutral live application feedback.
- [Tap exhale indicated](tap-390x844.jpg): actual pointer activation after the timed phase changed; no cycle restart.
- [Observe with reduced motion](observe-reduced-390x844.jpg): no interactive circle required, scaling disabled, textual cue/countdown retained.
- [Completion with mock feedback](completion-mock-390x844.jpg): saved completion and accurate Demo response label.
- [Grounding/feedback regression](grounding-feedback-regression-390x844.jpg): unchanged alternative skill and contextual mock response.

[Selected session evidence](session-evidence.json) contains eight known fictional sessions and three mock exchanges from the main verification identity, with that identity omitted. Every exported session's summary/status/duration was compared with its scoped GET response; SQLite was opened read-only. No raw pointer/key/tap events were stored or exported. Separate fresh identities were used for layout-only probes and are not part of this export.

| Run | Saved duration | Entry/setup | Mode | Inhale / exhale observations | Completed cycles |
| --- | --- | --- | --- | --- | --- |
| 8ebbaad5-490d-4b73-9108-3be64cccc601 | 60.007s | 0.001s | hold | 1 / 6 | 6 |
| 694c8ddb-e7c4-4062-bc54-5ec2f996976c | 60.010s | 0.001s | observe | 0 / 0 | 6 |
| ae546f36-60c6-4482-9baf-16e0cfd24e86 | 4.498s, exited | 0.001s | tap | 1 / 1 | 0 |

The Hold run included an early key release; it still completed normally. A released button at exhale onset counts as an observed released state. Counts indicate matching button state/tap at least once within a phase, not sustained adherence or actual breathing. Completed cycles are elapsed timed cycles, not proven breath cycles. No score or clinical interpretation is justified.

A developer hot reload interrupted one preliminary run, leaving session0bc4b705-a6e4-4991-b53e-f8a6c3cf519d marked started with NULL summary; it was retained and is not counted as a successful timing measurement. A fresh stable run provided the measured results above. Automated tests cover neutral held-exhale feedback, early release, duplicate events, mode changes, omitted/invalid summaries and tracking initialization/update faults. Full screen-reader/zoom and physical touch-device verification remain pending. See [complete verification](../../verification.md) for test commands, migration preservation, restart and limitations.
