// One primary hold interaction plus a native Start/Pause accessibility control.
// These controls advance guided time; they do not detect actual breathing.
export function createBreathingControl(timer) {
  let pointer = null, key = null
  function pause() { pointer = null; key = null; timer.pause() }
  return {
    pointerDown(id) {
      if (pointer !== null || key !== null) return
      pointer = id; timer.resume()
    },
    pointerUp(id) { if (id === pointer) pause() },
    keyDown(value, repeat = false) {
      if (![' ', 'Enter'].includes(value) || repeat || key !== null || pointer !== null) return
      key = value; timer.resume()
    },
    keyUp(value) { if (value === key) pause() },
    toggle(wasRunning = timer.snapshot().running) { if (wasRunning) pause(); else { pointer = null; key = null; timer.resume() } },
    pause,
    stop() { pointer = null; key = null; return timer.stop() },
  }
}
