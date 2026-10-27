// A recorder belongs to exactly one session. Old responses update only that
// recorder's state; they cannot replace a later session or block navigation.
export function createSessionRecorder({ api, payload, onState = () => {} }) {
  let started = false
  let ended = false
  let terminal = null
  let queue = Promise.resolve()
  let revision = 0
  async function ensureStarted() {
    if (!started) {
      await api.startSession(payload)
      started = true
    }
  }
  async function ensureEnded() {
    await ensureStarted()
    if (!ended) {
      await api.endSession(payload.id, terminal)
      ended = true
    }
  }
  function enqueue(label, task) {
    const request = ++revision
    onState(`${label} saving…`)
    queue = queue.then(task).then(
      () => { if (request === revision) onState(`${label} saved.`); return true },
      () => { if (request === revision) onState(`${label} not saved. You can keep using Pause.`); return false },
    )
    return queue
  }
  return {
    start() { return enqueue('Session', ensureStarted) },
    finish(value) {
      if (terminal) return queue
      terminal = Object.freeze({ ...value })
      return enqueue('Session', ensureEnded)
    },
    feedback(value) {
      if (terminal?.status !== 'completed') return queue
      return enqueue('Feedback', async () => {
        await ensureEnded()
        await api.saveFeedback(payload.id, value)
      })
    },
    settled() { return queue },
  }
}
