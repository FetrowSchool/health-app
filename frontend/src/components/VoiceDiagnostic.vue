<script setup>
import { ref } from 'vue'
import VoicePanel from './VoicePanel.vue'
import CrisisScreen from './CrisisScreen.vue'
import { createDiagnosticAPI, probeMicrophone } from '../voiceDiagnostic.js'
const crisis = ref(false), checking = ref(false), microphone = ref('Not checked in this run.'), status = ref('closed'), stages = ref([])
async function checkMic() {
  checking.value = true
  microphone.value = 'Waiting for microphone permission. No session will be created.'
  try { microphone.value = await probeMicrophone() } finally { checking.value = false }
}
function diagnostic(event) { stages.value = [...stages.value, event].slice(-50) }
</script>
<template>
  <div class="app-shell">
    <header class="app-header"><strong>Pause diagnostic</strong><button class="secondary crisis-button" @click="crisis = true">Crisis Support</button></header>
    <main>
      <CrisisScreen v-if="crisis" @return="crisis = false" />
      <section v-else class="home-content" aria-labelledby="screen-heading">
        <h1 id="screen-heading">Isolated voice test</h1>
        <p>No SQLite, history, recommendations, backend reasoning or tools.</p>
        <p>Microphone check is free. Use microphone creates a paid Live session on port 8001. Start only after approval; no automatic retry.</p>
        <button class="secondary wide" :disabled="checking || !['closed','error'].includes(status)" @click="checkMic">Check microphone only</button>
        <p role="status">{{ microphone }}</p>
        <VoicePanel v-if="!checking" :api-factory="createDiagnosticAPI" :on-diagnostic="diagnostic" @state="status = $event" />
        <details><summary>Sanitized connection stages</summary><ol><li v-for="(event,index) in stages" :key="index">{{ event.stage }} · {{ event.category }}</li></ol></details>
        <a class="secondary wide" href="/">Return to Pause</a>
      </section>
    </main>
  </div>
</template>
