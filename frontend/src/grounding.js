// Fixed reviewed steps. No provider output, timers, or disclosures enter this state.
export const GROUNDING_STEPS = Object.freeze([
  Object.freeze({ sense: 'Sight', instruction: 'Notice 5 things you can see.', count: 5, seconds: 20 }),
  Object.freeze({ sense: 'Touch', instruction: 'Notice 4 things you can feel.', count: 4, seconds: 15 }),
  Object.freeze({ sense: 'Hearing', instruction: 'Notice 3 things you can hear.', count: 3, seconds: 15 }),
  Object.freeze({ sense: 'Smell', instruction: 'Notice 2 things you can smell.', count: 2, seconds: 10 }),
  Object.freeze({ sense: 'Taste', instruction: 'Notice 1 thing you can taste.', count: 1, seconds: 10 }),
])
export function createGroundingProgress() {
  return GROUNDING_STEPS.map(step => Array(step.count).fill(false))
}
export function toggleNoticed(progress, step, item) {
  if (!Number.isInteger(step) || !Number.isInteger(item) || !GROUNDING_STEPS[step] || item < 0 || item >= GROUNDING_STEPS[step].count) return
  progress[step][item] = !progress[step][item]
}
