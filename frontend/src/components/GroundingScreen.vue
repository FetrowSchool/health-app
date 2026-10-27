<script setup>
import { computed, nextTick, onMounted, reactive, ref, watch } from 'vue'
import { GROUNDING_STEPS, createGroundingProgress, toggleNoticed } from '../grounding.js'
const emit = defineEmits(['started', 'exit', 'finish'])
const step = ref(0)
const heading = ref(null)
const progress = reactive(createGroundingProgress())
const currentStep = computed(() => GROUNDING_STEPS[step.value])
const noticed = computed(() => progress[step.value].filter(Boolean).length)
onMounted(() => emit('started', { startClock: performance.now(), startedAt: new Date().toISOString() }))
watch(step, async () => { await nextTick(); heading.value?.focus() })
function continueStep() {
  if (step.value < GROUNDING_STEPS.length - 1) step.value++
  else emit('finish')
}
</script>
<template>
  <section class="exercise-content grounding-content" aria-labelledby="screen-heading">
    <div class="exercise-top"><p class="eyebrow">5-4-3-2-1 Grounding</p><button type="button" class="exit" @click="$emit('exit')">Exit</button></div>
    <div class="grounding-step">
      <p class="progress-label">Step {{ step + 1 }} of 5 · {{ currentStep.sense }}</p>
      <div class="segments five" aria-hidden="true"><span v-for="index in 5" :key="index" :class="{ current: index === step + 1, past: index < step + 1 }"></span></div>
      <h1 ref="heading" id="screen-heading" tabindex="-1">{{ currentStep.instruction }}</h1>
      <p class="muted">Tap a circle for each item you notice. Tap again to undo.</p>
      <div class="notice-circles" role="group" :aria-label="`${currentStep.sense}: things noticed`">
        <button v-for="(selected, index) in progress[step]" :key="`${step}-${index}`" type="button" class="notice-circle" :aria-label="`Mark item ${index + 1} noticed`" :aria-pressed="selected" @click="toggleNoticed(progress, step, index)">
          <span aria-hidden="true">{{ selected ? '✓' : index + 1 }}</span>
        </button>
      </div>
      <p class="noticed-count" role="status">{{ noticed }} of {{ currentStep.count }} noticed</p>
    </div>
    <div class="step-actions">
      <p class="permission">You can skip any step. Continue when you’re ready.</p>
      <div class="button-pair">
        <button v-if="step > 0" type="button" class="secondary" @click="step--">Back</button>
        <button type="button" class="primary" @click="continueStep">Continue <span aria-hidden="true">→</span></button>
      </div>
    </div>
  </section>
</template>
