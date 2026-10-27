<script setup>
defineProps({ name: { type: String, required: true } })
</script>
<template>
  <svg viewBox="0 0 32 32" aria-hidden="true" focusable="false">
    <template v-if="name === 'conversation'">
      <path d="M7 6h18a3 3 0 0 1 3 3v11a3 3 0 0 1-3 3H13l-7 5v-5a3 3 0 0 1-3-3V9a3 3 0 0 1 4-3Z" /><path d="M9 14h2m4 0h2m4 0h2" />
    </template>
    <template v-else-if="name === 'breathing'">
      <circle cx="16" cy="16" r="11" /><path d="M9 16h14M16 9v14" />
    </template>
    <template v-else-if="name === 'grounding'">
      <path d="M3 16s5-8 13-8 13 8 13 8-5 8-13 8S3 16 3 16Z" /><circle cx="16" cy="16" r="4" />
    </template>
    <path v-else-if="name === 'calm'" d="M5 12h22M5 19h22M9 25h14" />
    <template v-else-if="name === 'okay'">
      <circle cx="16" cy="16" r="11" /><path d="M10 13h1M21 13h1M11 21h10" />
    </template>
    <path v-else-if="name === 'anxious'" d="M4 16c4-12 8 12 12 0s8 12 12 0" />
    <path v-else d="M4 12c4-9 8 9 12 0s8 9 12 0M4 21c4-9 8 9 12 0s8 9 12 0" />
  </svg>
</template>
