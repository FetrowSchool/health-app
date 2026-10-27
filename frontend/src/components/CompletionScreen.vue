<script setup>
defineProps({ feedback: { type: String, default: '' }, saveState: { type: String, default: '' }, response: { type: Object, default: () => ({ status: 'idle', text: '', label: '' }) } })
defineEmits(['home', 'feedback'])
const options = [{ label: 'Helpful', value: 'helpful' }, { label: 'Not Helpful', value: 'not_helpful' }, { label: 'Skip', value: 'skipped' }]
</script>
<template>
  <section class="completion-content" aria-labelledby="completion-heading">
    <p class="eyebrow">Finished</p>
    <h1 id="completion-heading" tabindex="-1">Exercise complete.</h1>
    <div class="feedback-block">
      <h2>Was this helpful?</h2><p class="muted">Feedback is optional.</p>
      <div class="feedback-options" role="group" aria-label="Optional exercise feedback">
        <button v-for="option in options" :key="option.value" type="button" class="secondary" :aria-pressed="feedback === option.value" @click="$emit('feedback', option.value)">{{ option.label }}</button>
      </div>
      <p class="feedback-status" role="status">{{ saveState }}</p>
    </div>
    <div v-if="response.status !== 'idle'" class="conversation-response" role="status" aria-live="polite">
      <p class="response-label">{{ response.label }}</p>
      <p v-if="response.text" class="response-copy">{{ response.text }}</p>
    </div>
    <button type="button" class="primary wide return-home" @click="$emit('home')">Return Home <span aria-hidden="true">→</span></button>
  </section>
</template>
