<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { breathingState, createBreathingTimer } from '../exerciseTiming.js'
import { createBreathingControl } from '../breathingInteraction.js'
const emit = defineEmits(['started', 'exit', 'complete'])
const state = ref({ ...breathingState(0), started: false, running: false, wallMs: 0 })
const deviceReduced = ref(false), manualReduced = ref(false)
const reduced = computed(() => deviceReduced.value || manualReduced.value)
const phaseLabel = computed(() => state.value.phase === 'in' ? 'Breathe In' : 'Breathe Out')
const instruction = computed(() => !state.value.started ? 'Press and hold to begin.'
  : state.value.running ? 'Release or select Pause to pause.' : 'Paused — press and hold to continue.')
const activeClock = computed(() => `${Math.floor(state.value.activeMs / 60000)}:${String(Math.floor(state.value.activeMs / 1000) % 60).padStart(2, '0')}`)
const timer = createBreathingTimer({
  now: () => performance.now(), schedule: fn => requestAnimationFrame(fn), cancel: id => cancelAnimationFrame(id),
  onUpdate: value => { state.value = value },
  onStarted: startClock => emit('started', { startClock, startedAt: new Date().toISOString() }),
})
const control = createBreathingControl(timer)
let preference, alternativeIntent = null
function alternativeDown() { alternativeIntent = state.value.running }
function toggleAlternative() { control.toggle(alternativeIntent ?? state.value.running); alternativeIntent = null }
function alternativeBlur() { alternativeIntent = null; control.pause() }
function syncMotion(event) { deviceReduced.value = event.matches }
function pointerDown(event) {
  if (!event.isPrimary || event.button !== 0) return
  control.pointerDown(event.pointerId)
  try { event.currentTarget.setPointerCapture(event.pointerId) } catch { /* Global release/blur still pause. */ }
}
function pointerEnd(event) { control.pointerUp(event.pointerId) }
function keyDown(event) { if ([' ', 'Enter'].includes(event.key)) { event.preventDefault(); control.keyDown(event.key, event.repeat) } }
function keyUp(event) { if ([' ', 'Enter'].includes(event.key)) { event.preventDefault(); control.keyUp(event.key) } }
function releaseKey(event) { control.keyUp(event.key) }
function pauseWhenHidden() { if (document.visibilityState === 'hidden') control.pause() }
function stop() { control.stop(); return timer.summary() }
function finish() { if (state.value.started) { stop(); emit('complete') } }
defineExpose({ stop, pause: control.pause })
onMounted(() => {
  preference = window.matchMedia('(prefers-reduced-motion: reduce)')
  deviceReduced.value = preference.matches
  preference.addEventListener('change', syncMotion)
  window.addEventListener('blur', control.pause)
  window.addEventListener('pointerup', pointerEnd)
  window.addEventListener('pointercancel', pointerEnd)
  window.addEventListener('keyup', releaseKey)
  document.addEventListener('visibilitychange', pauseWhenHidden)
})
onUnmounted(() => {
  control.stop()
  preference?.removeEventListener('change', syncMotion)
  window.removeEventListener('blur', control.pause)
  window.removeEventListener('pointerup', pointerEnd)
  window.removeEventListener('pointercancel', pointerEnd)
  window.removeEventListener('keyup', releaseKey)
  document.removeEventListener('visibilitychange', pauseWhenHidden)
})
</script>
<template>
  <section class="exercise-content breathing-content" aria-labelledby="screen-heading">
    <div class="exercise-top"><h1 id="screen-heading" class="eyebrow" tabindex="-1">Paced Breathing</h1><button type="button" class="exit" @click="$emit('exit')">Exit</button></div>
    <div class="breathing-stage">
      <div class="breathing-visual" aria-hidden="true" :class="{ 'motion-reduced': reduced }" :style="{ transform: `scale(${0.76 + 0.24 * state.expansion})` }"></div>
      <div class="breathing-copy"><h2 aria-live="polite" aria-atomic="true">{{ state.started ? phaseLabel : 'Ready' }}</h2><p>{{ state.started ? `${state.seconds} ${state.seconds === 1 ? 'second' : 'seconds'}` : 'Press and hold' }}</p></div>
      <button type="button" class="breathing-input" :aria-label="`Breathing circle: ${instruction}`" aria-describedby="breathing-instruction" @pointerdown="pointerDown" @pointerup="pointerEnd" @pointercancel="pointerEnd" @lostpointercapture="pointerEnd" @keydown="keyDown" @keyup="keyUp" @blur="control.pause" @click.prevent></button>
    </div>
    <p id="breathing-instruction" class="breathing-instruction" role="status">{{ instruction }}</p>
    <p class="planned-notice" role="status">{{ state.plannedComplete ? 'Planned exercise complete. Finish or continue optionally.' : 'Planned portion: six cycles · 60 active seconds.' }}</p>
    <p class="progress-label">Active {{ activeClock }} · {{ Math.min(state.completedCycles, 6) }} of 6 planned cycles<span v-if="state.plannedComplete"> · optional cycle {{ state.cycle - 6 }}</span></p>
    <div class="segments six" aria-hidden="true"><span v-for="index in 6" :key="index" :class="{ current: index === state.cycle && !state.plannedComplete, past: index <= state.completedCycles }"></span></div>
    <button type="button" class="primary wide breathing-finish" :disabled="!state.started" @click="finish">Finish</button>
    <button type="button" class="breathing-alternative" :aria-pressed="state.running" @pointerdown="alternativeDown" @pointercancel="alternativeIntent = null" @click="toggleAlternative" @blur="alternativeBlur">{{ state.running ? 'Pause' : 'Start without holding' }}</button>
    <button type="button" class="motion-control" :aria-pressed="reduced" :disabled="deviceReduced" @click="manualReduced = !manualReduced">Reduced motion <strong>{{ reduced ? 'On' : 'Off' }}</strong><span v-if="deviceReduced"> · device setting</span></button>
  </section>
</template>
