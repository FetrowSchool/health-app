<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { createVoiceAPI } from '../api.js'
import { createVoiceSession } from '../voiceSession.js'
import { bindVoiceLifecycle } from '../voiceLifecycle.js'

const props = defineProps({ apiFactory: Function, onDiagnostic: Function })
const emit = defineEmits(['state'])
const audio = ref(null)
const state = ref({ status: 'closed', message: 'Microphone off. Start when you’re ready.', audioBlocked: false })
const detail = computed(() => state.value.message.replace(/(?:the )?text choices/gi,
  text => /^[A-Z]/.test(text) ? 'Other Pause features' : 'other Pause features'))
const labels = { permission: 'Permission', connecting: 'Connecting', active: 'Active', muted: 'Muted', closing: 'Closing', closed: 'Closed', error: 'Error' }
const running = computed(() => ['permission', 'connecting', 'active', 'muted'].includes(state.value.status))
let voice, lifecycle
defineExpose({ end: () => lifecycle?.leave() })
onMounted(() => {
  voice = createVoiceSession({ api: (props.apiFactory || createVoiceAPI)(), audio: audio.value, onDiagnostic: props.onDiagnostic,
    onState: value => { state.value = value; emit('state', value.status) } })
  lifecycle = bindVoiceLifecycle(voice)
})
onBeforeUnmount(() => {
  lifecycle?.dispose()
})
</script>
<template>
  <section class="voice-panel" aria-label="Optional voice conversation">
    <p class="voice-status" role="status" aria-live="polite" aria-atomic="true">Voice: {{ labels[state.status] }}<span v-if="['active', 'muted'].includes(state.status)"> · Live model</span></p>
    <p id="voice-detail" class="voice-detail">{{ detail }}</p>
    <button v-if="!running" type="button" class="secondary wide voice-microphone" :disabled="state.status === 'closing'" aria-describedby="voice-detail voice-privacy" @click="voice?.start()">
      <svg viewBox="0 0 24 24" aria-hidden="true"><rect x="9" y="2" width="6" height="12" rx="3" /><path d="M5 10v1a7 7 0 0 0 14 0v-1M12 18v4M8 22h8" /></svg>
      Use microphone
    </button>
    <div v-else class="voice-actions">
      <button v-if="['active', 'muted'].includes(state.status)" type="button" class="secondary" :aria-pressed="state.status === 'muted'" @click="voice.toggleMute()">{{ state.status === 'muted' ? 'Unmute microphone' : 'Mute microphone' }}</button>
      <button type="button" class="secondary" @click="voice.stop()">{{ state.status === 'permission' || state.status === 'connecting' ? 'Cancel voice' : 'End voice' }}</button>
    </div>
    <button v-if="state.audioBlocked && running" type="button" class="secondary wide voice-enable" @click="voice.enableAudio()">Enable assistant audio</button>
    <p id="voice-privacy" class="voice-detail voice-privacy">External AI voice. Mute does not stop playback, the session or billing. End to finish. Transcripts appear only in this view; Pause saves no audio or transcripts.</p>
    <section v-if="state.transcripts?.length" class="voice-transcripts" aria-label="Live transcript">
      <p class="voice-detail">Live transcript · temporary, may contain errors</p>
      <div v-for="(segment, index) in state.transcripts" :key="index" class="voice-transcript-segment">
        <strong>{{ segment.speaker }}</strong>
        <small>{{ segment.start_ms }}–{{ segment.end_ms }} ms</small>
        <p>{{ segment.text }}</p>
      </div>
    </section>
    <audio ref="audio" playsinline></audio>
  </section>
</template>
