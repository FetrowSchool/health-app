<script setup>
defineProps({ active: Boolean })
defineEmits(['support'])
</script>
<template>
  <header class="app-header">
    <span class="brand">Pause</span>
    <span v-if="active" class="support-label">Crisis Support</span>
    <button v-else type="button" class="crisis" @click="$emit('support')">Crisis Support</button>
  </header>
</template>
