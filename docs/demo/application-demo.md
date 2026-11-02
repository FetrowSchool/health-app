# Pause — finished application demonstration

Prepared November2, 2026. **Outline only: no recording has been created.** Aim for about4–5 minutes, adjusting to the instructor's actual duration/format requirements. Capability labels below map to the requested features, not invented rubric numbers.

## Before recording

- Follow [README startup instructions](../../README.md#local-setup-and-startup). Use the current working tree: plain HEAD does not yet include the uncommitted History work. Do not present an older checkout as the current app. Check the [complete verification evidence](../evidence/part-3-3-clean/index.md) before making claims.
- Use a separate recording browser profile/private window and keep it open through refresh/restart. This gives a separate local identity and daily check-in without deleting existing storage or records. Keep the same origin throughout. Only fictional sessions should appear in this profile's History; inspect it before recording. Do not show another profile's records.
- For reproducible text feedback, use `MODEL_PROVIDER=mock`. When starting a recording backend yourself, this process-only command also limits voice to30 active seconds, without editing saved settings:

  ```sh
  MODEL_PROVIDER=mock VOICE_SESSION_DURATION_SECONDS=30 backend/.venv/bin/python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
  ```

  First stop the existing review backend normally, after ending voice/exercises; do not start a second process on the same port. This still reads any existing server-side voice key, so **Use microphone can incur charges** even with mock text mode. No key is needed for the other features. After recording, restart using the ordinary README command to restore saved configuration.
- Set a390×844 browser viewport. Enlarge code/terminal text separately for legibility. Close notifications, unrelated tabs, `.env`, developer request payloads, credentials, raw SDP and private records. Do not expose a private recording share link or access token in the capture.
- Check system/browser microphone permission and recording-system audio routing before a planned voice take. The existing diagnostic's **Check microphone only** action can test capture/release without a provider call; it is different from **Use microphone**. See [diagnostic instructions](../../README.md#isolated-gpt-live-diagnostic-no-paid-request-on-load). Do not start a provider session merely to test permission.
- A new voice take is billable and must be an intentional, separately approved action if an agent operates it. The previous one-attempt approval was consumed. No new model call is part of preparing these materials. Use the fallback evidence below if another live take is not approved.

## Recording outline

| Section / approximate time | What to show | What to say briefly | Requirement demonstrated | Setup needed |
| --- | --- | --- | --- | --- |
| **1. Application launch —15s** | Briefly show running Vue/FastAPI, then the app. Avoid a long install sequence. | “Pause uses Vue, FastAPI and SQLite. This is a coursework prototype; the exercises also work without a live model.” | Runnable application; frontend/backend/data separation. | Start/warm services before the take. A fresh install is already documented; do not claim this recording repeats it unless it does. |
| **2. Daily mood —10s** | First opening's four choices, Skip and close. Use Skip, or a fictional Okay choice. Later reload briefly if needed to show no repeated same-day popup. | “This daily check-in is optional. I can skip it and continue without entering personal information.” | Skippable check-in, low input demand, daily persistence. | Fresh recording profile/origin for today's popup; don't reset another profile's identity. |
| **3. Home —10s** | Stop to chat, both exercise cards, History and persistent support. Tab to a card to show focus. | “Both exercises stay directly available. The assistant does not choose or start one for me.” | Clear mobile navigation, keyboard focus, user control. |390×844; current working-tree build. |
| **4. Paced Breathing —75–85s** | Ready before input; hold for a few seconds, release to pause, resume. While paused, set Reduced motion; then use Start without holding to continue the planned portion. At the six-cycle notice choose Finish, then Helpful for a mock text reply. | “Holding advances the cue; release pauses it. Six four-second inhales and six six-second exhales make60 active seconds. Pauses add wall time. Finish is my choice, and button use does not measure actual breathing. This reply is labeled mock.” | Closed-loop interaction, fixed app timing, accessible alternative, immediate feedback, optional post-exercise response/persistence. | Keep the planned60 active seconds honest. If editing the wait, visibly label the time cut; do not make a shortened take look like a real60s run. Leave one completed session and one mock exchange for History. |
| **5. Grounding (5-4-3-2-1) —20–30s** | All five senses in order; toggle/undo one counter, Continue without filling it, Back preserves it. Finish; Skip optional feedback. Optionally show a second brief session's Exit. | “The app presents five seen, four felt, three heard, two smelled and one tasted. Counters and steps can be skipped. I control Continue, Back and Exit.” | Fixed reviewed steps, optional interaction, immediate exit, completed versus exited status. | This is a quick navigation walkthrough, not a claim that sensory observation always takes20 seconds. Preserve the app's instructions. |
| **6. AI conversation entry —10s** | Home → Stop to chat → Talk to Pause in Closed state, Home/support still available. Point back to the saved text feedback from section4. | “This screen provides optional voice conversation. Text AI is the short post-exercise feedback already shown; this version has no typed-chat composer.” | Accurate AI scope, optional entry, text alternative/feedback, honest source labels. | Opening this screen does not start capture or a model session. Do not invent a typed conversation feature. |
| **7. GPT-Live-1 voice —30–45s** | Only if a new live take is approved: Use microphone → permission/Connecting → Active. Speak the fictional script below; briefly mute/unmute, then End and wait for confirmed closure. | “Active means the session has started. Mute stops my outgoing microphone only; End closes the conversation. The app controls exercises and support, and saves no voice audio or transcripts.” | Actual live-model integration, user control, cleanup and source honesty. | Existing ignored server-side key, microphone/output routing, intentional billable action, quiet room. No automatic retry. Show Enable assistant audio if playback is blocked. Never label a mock take as live. |
| **8. Independent Crisis Support —15–20s** | Open support, point out regional scope and Return Home. For independence, briefly stop only the demo backend, open support again, then restart it. | “This information is a local route, independent of AI or a classifier. It remains available when the backend is unavailable.” | Persistent independent support, graceful service failure, clear regional limits. | End voice first; never operate a contact link for the recording. If using earlier offline evidence instead, label its date and provenance. The health footer is a startup snapshot, not continuous health. |
| **9. History —20–25s** | Recent exercises with completed/exited status and active/total time. Open the saved mock feedback conversation; show user then assistant and its source. | “History shows saved exercise records and text feedback in order. Voice conversations are not stored here.” | Saved history, truthful durations/status/source, conversation order. | Only the recording profile's fictional records. A completed session with Helpful exists from section4; an Exit creates the contrasting status. |
| **10. SQLite/personalization —25–35s** | Refresh/restart the demo backend and reopen the same History. Show a read-only query for only the two known fictional session IDs. Return Home to Recently used after the most recent supported completion. | “These saved rows survive a backend restart. Recently used comes from the latest completed exercise. It does not diagnose mood or automatically reorder/start the two cards.” | Durable SQLite relationships, read-only retrieval, lightweight transparent personalization. | Wait for Session/Feedback saved before restart; if a save failed, show that honestly. Keep the browser profile/origin/identity unchanged; don't reseed/delete data. Prepare the scoped read-only query below; do not show SELECT * from an existing private database. |

## Fictional voice script and fallback

For a newly approved take, use only:

1. “This is a fictional schoolwork example. I'm putting off an assignment. What is one small next step?”
2. “Which existing Pause exercise could I try?”
3. Interrupt: “Actually, no exercise. Let's keep this practical.”

Keep the script within the short session limit; if not completed, say which part was not demonstrated. Respect any permission/playback error; return Home or use support, with no automatic second attempt. Mute/unmute once, select End, and show the actual close result. If closure is unconfirmed, say so; do not infer a billing-stop guarantee from Mute or a hangup acceptance.

The [November2 approved attempt](../evidence/part-3-3-clean/approved-live-outcome.json) actually returned provider201 in1151ms, reached Active, received assistant output and automatically closed with session.closed/microphone-off UI observed by39.319s. **It did not complete this three-turn script, independently score audibility, or test real manual Mute/End.** Its screenshot was excluded because incidental non-script speech appeared. If not making a new paid take, show the [sanitized transport evidence](../evidence/part-3-3-clean/live-transport.txt), identify it as earlier evidence, and state that a new live conversation was not recorded. This fallback is not equivalent to filming a new voice interaction; check the instructor's demonstration requirement.

Suggested closing sentence: “The app's fixed exercises, saved History and independent support are working. The evaluation still documents voice-content validation and full screen-reader/zoom limits.” Do not claim that all safety checks passed: unsupported-exercise and professional-therapy transcript claims remain unfiltered in the voice path, although the text-feedback catalog and app-control boundaries reject invalid actions. See [behavior checks](../evaluation/behavior-checks.md).

## Scoped SQLite view

Use a read-only SQLite viewer/connection to `data/app.sqlite3`. Replace placeholders with only the session/conversation IDs created in this recording; they are record IDs, not credentials. Do not run this with literal placeholders and claim rows were found.

```sql
SELECT id, exercise_type, status, duration_seconds, active_duration_seconds,
       optional_continuation_seconds, feedback
FROM exercise_sessions
WHERE id IN ('<recorded-breathing-id>', '<recorded-grounding-id>')
ORDER BY started_at;

SELECT c.id AS conversation_id, c.session_id, c.provider_mode, c.status,
       m.ordinal, m.role, m.content
FROM conversations c JOIN messages m ON m.conversation_id = c.id
WHERE c.id = '<recorded-text-feedback-conversation-id>'
ORDER BY m.ordinal;
```

If the selected records contain anything beyond fictional test data, stop and choose the proper fixture/profile rather than masking a different person's data as a demonstration. Existing [fictional SQL/API/UI evidence](../evidence/part-3-3-clean/database-evidence.json) can be shown with an “earlier November2 verification” label; do not present its rows as newly created by the recording.

## Recording checklist for both videos

- [ ] Confirm the instructor's actual duration/file/link rules; this outline supplies suggested timings only.
- [ ] Start the correct app copy; check backend readiness, mock text mode and recording origin. Keep a fresh fictional-data profile open.
- [ ] Check microphone permission without a provider session; test recorder narration/system audio. Start any billable voice session only intentionally/with fresh approval for agent operation.
- [ ] Hide `.env`, keys, authorization/SDP payloads, notifications, unrelated history and private tabs. Use only the fictional script; stop/exclude accidental private speech.
- [ ] Record the ten application sections, including working save/source labels and optional controls. End voice and confirm the actual result.
- [ ] Record the [process screencast](process-screencast.md): actual dated failure evidence, uncertainty, verified outcome and the breathing-code explanation.
- [ ] Save two real recordings, for example `pause-application-demo.mp4` and `pause-process-screencast.mp4`. These are suggested future filenames; neither file has been created by this task.
- [ ] Watch both recordings from beginning to end. Check audible narration/assistant audio, readable text/cursor, no missing sections/private content, and truthful labels on edits, mocks and historical evidence.
- [ ] Add accurate captions/transcript; describe important visual-only state changes aloud. Confirm captions and video playback work.
- [ ] Upload to the course-approved location, create descriptive viewer links, set the intended audience's access, and test access from a signed-out/separate viewer as appropriate. Do not expose an API key or private access token while doing so.
- [ ] Add the **actual** working links after upload. Current status: application recording **not recorded/not linked**; process recording **not recorded/not linked**. No placeholder URL or fake recording is supplied.
