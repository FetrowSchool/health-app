<script setup>
import SkillIcon from './SkillIcon.vue'
defineEmits(['choose', 'conversation'])
</script>
<template>
  <section class="home-content" aria-labelledby="screen-heading">
    <p class="eyebrow">Your moment</p>
    <h1 id="screen-heading" tabindex="-1">Take a moment.</h1>
    <p class="muted">Chat with Pause or choose an exercise.</p>
    <div class="exercise-cards">
      <button type="button" class="exercise-card" @click="$emit('conversation')">
        <span class="icon-tile"><SkillIcon name="conversation" /></span>
        <span><strong>Stop to chat</strong><small>Ai assistant conversation</small></span>
        <span class="arrow" aria-hidden="true">↗</span>
      </button>
      <button type="button" class="exercise-card" @click="$emit('choose', 'breathing')">
        <span class="icon-tile"><SkillIcon name="breathing" /></span>
        <span><strong>Paced Breathing</strong><small>About 60 seconds</small></span>
        <span class="arrow" aria-hidden="true">↗</span>
      </button>
      <button type="button" class="exercise-card" @click="$emit('choose', 'grounding')">
        <span class="icon-tile"><SkillIcon name="grounding" /></span>
        <span><strong>5-4-3-2-1 Grounding</strong><small>About 60–75 seconds</small></span>
        <span class="arrow" aria-hidden="true">↗</span>
      </button>
    </div>
  </section>
</template>
