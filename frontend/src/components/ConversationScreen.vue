<script setup>
import { ref } from 'vue'
import VoicePanel from './VoicePanel.vue'
defineEmits(['home'])
const voicePanel = ref(null)
defineExpose({ endVoice: () => voicePanel.value?.end() })
</script>
<template>
  <section class="conversation-content" aria-labelledby="screen-heading">
    <p class="eyebrow">AI conversation</p>
    <h1 id="screen-heading" tabindex="-1">Talk to Pause</h1>
    <p class="conversation-intro">Use the microphone to talk with Pause.</p>
    <VoicePanel ref="voicePanel" />
    <button type="button" class="secondary wide conversation-home" @click="$emit('home')">Return Home</button>
  </section>
</template>
