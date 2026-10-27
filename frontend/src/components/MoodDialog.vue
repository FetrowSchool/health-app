<script setup>
import { onMounted, ref } from 'vue'
import SkillIcon from './SkillIcon.vue'
defineProps({ storageAvailable: Boolean })
const emit = defineEmits(['dismiss', 'support'])
const dialog = ref(null)
const options = ['Calm', 'Okay', 'Anxious', 'Overwhelmed']
onMounted(() => dialog.value.showModal())
</script>
<template>
  <dialog ref="dialog" class="mood-dialog" aria-labelledby="mood-heading" aria-describedby="mood-note" @cancel.prevent="emit('dismiss')">
    <div class="dialog-top">
      <p class="eyebrow">Daily check-in</p>
      <button type="button" class="close" aria-label="Close check-in and skip" @click="emit('dismiss')">×</button>
    </div>
    <h2 id="mood-heading" tabindex="-1" autofocus>How are you feeling right now?</h2>
    <p id="mood-note" class="muted">You can skip this check-in.</p>
    <div class="mood-options">
      <button v-for="mood in options" :key="mood" type="button" class="mood-choice" @click="emit('dismiss', mood.toLowerCase())">
        <SkillIcon :name="mood.toLowerCase()" />{{ mood }}
      </button>
    </div>
    <button type="button" class="secondary wide" @click="emit('dismiss')">Skip</button>
    <div class="dialog-safety"><button type="button" class="crisis" @click="emit('support')">Crisis Support</button></div>
    <p v-if="!storageAvailable" class="storage-note">This browser cannot remember check-ins after you leave.</p>
    <p class="prototype">Coursework prototype — not a mental health support service.</p>
  </dialog>
</template>
