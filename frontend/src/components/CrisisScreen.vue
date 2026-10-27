<script setup>
defineProps({ returnToCompletion: Boolean })
defineEmits(['return'])
</script>
<template>
  <section class="crisis-content" aria-labelledby="screen-heading">
    <p class="eyebrow">U.S. resources</p>
    <h1 id="screen-heading" tabindex="-1">Crisis support</h1>
    <p class="geography">For the United States and its territories. These are not worldwide resources.</p>
    <h2>988 Suicide &amp; Crisis Lifeline</h2>
    <div class="support-options">
      <a class="primary" href="tel:988?oai_link_source=model_response_hotline">Call 988 <span aria-hidden="true">↗</span></a>
      <a class="secondary" href="sms:988?oai_link_source=model_response_hotline">Text 988</a>
      <a class="secondary" href="https://988lifeline.org/chat/?oai_link_source=model_response_hotline" target="_blank" rel="noopener noreferrer">Online chat <span class="new-tab">(new tab)</span></a>
    </div>
    <p class="muted">You can also visit <a href="https://988lifeline.org?oai_link_source=model_response_hotline" target="_blank" rel="noopener noreferrer">988lifeline.org (new tab)</a>. Calls, texts, and chat need a compatible device and connection.</p>
    <p class="muted">Outside this region, use crisis resources for your location.</p>
    <p class="safety-boundary">Pause does not provide therapy, professional support, or emergency monitoring. No one is monitoring your use of this coursework prototype.</p>
    <button type="button" class="secondary wide" @click="$emit('return')">{{ returnToCompletion ? 'Return to completion' : 'Return Home' }}</button>
  </section>
</template>
