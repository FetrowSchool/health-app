export const PLANNED_DURATION_MS = 60_000

// This is active guided time, not a measurement of respiration.
export function breathingState(activeMs) {
  const elapsed = Math.max(0, activeMs)
  const withinCycle = elapsed % 10_000
  const inhale = withinCycle < 4_000
  return {
    activeMs: elapsed,
    plannedComplete: elapsed >= PLANNED_DURATION_MS,
    completedCycles: Math.floor(elapsed / 10_000),
    cycle: Math.floor(elapsed / 10_000) + 1,
    phase: inhale ? 'in' : 'out',
    seconds: Math.ceil((inhale ? 4_000 - withinCycle : 10_000 - withinCycle) / 1_000),
    expansion: inhale ? withinCycle / 4_000 : 1 - (withinCycle - 4_000) / 6_000,
  }
}

// RAF renders only while active. Pauses accumulate no time; callbacks from an
// earlier run cannot restart a paused/finished timer. There is no automatic end.
export function createBreathingTimer({ now, schedule, cancel, onUpdate, onStarted = () => {} }) {
  let started = false, running = false, stopped = false
  let accumulated = 0, runAt = 0, firstAt = 0, endedAt = 0, frame = null, generation = 0
  function snapshot() {
    const time = stopped ? endedAt : now()
    const activeMs = accumulated + (running ? Math.max(0, time - runAt) : 0)
    return { ...breathingState(activeMs), started, running, wallMs: started ? Math.max(0, time - firstAt) : 0 }
  }
  const publish = () => { const value = snapshot(); onUpdate(value); return value }
  function clearFrame() { generation++; if (frame !== null) cancel(frame); frame = null }
  function tick(token) {
    if (!running || stopped || token !== generation) return
    publish()
    frame = schedule(() => tick(token))
  }
  function pause() {
    if (running) { accumulated += Math.max(0, now() - runAt); running = false }
    clearFrame()
    return publish()
  }
  return {
    snapshot,
    resume() {
      if (running || stopped) return
      runAt = now()
      const first = !started
      if (first) { started = true; firstAt = runAt }
      running = true
      if (first) onStarted(runAt)
      tick(++generation)
    },
    pause,
    stop() {
      if (!stopped) { pause(); endedAt = now(); stopped = true }
      return snapshot()
    },
    summary() {
      const active = Math.floor(snapshot().activeMs) / 1000
      return { active_duration_seconds: active, optional_continuation_seconds: Math.round(Math.max(0, active - 60) * 1000) / 1000,
        active_completed_cycles: Math.floor(active / 10) }
    },
  }
}
