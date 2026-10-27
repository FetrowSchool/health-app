<script setup>
import { nextTick, onMounted, onUnmounted, reactive, ref, shallowRef } from 'vue'
import SafetyHeader from './components/SafetyHeader.vue'
import MoodDialog from './components/MoodDialog.vue'
import HomeScreen from './components/HomeScreen.vue'
import ConversationScreen from './components/ConversationScreen.vue'
import BreathingScreen from './components/BreathingScreen.vue'
import GroundingScreen from './components/GroundingScreen.vue'
import CompletionScreen from './components/CompletionScreen.vue'
import CrisisScreen from './components/CrisisScreen.vue'
import { createDailyCheckIn, localDateKey } from './composables/dailyCheckIn.js'
import { applicationIdentity } from './composables/appIdentity.js'
import { createFeedbackResponder } from './feedbackResponse.js'
import { createSessionRecorder } from './sessionRecorder.js'
import { createActivityAPI, getHealth } from './api.js'

const checkIn = createDailyCheckIn()
const activityAPI = createActivityAPI(applicationIdentity())
const screen = ref('home')
const conversationScreen = ref(null)
const breathingScreen = ref(null)
const moodOpen = ref(!checkIn.isDismissed())
const storageAvailable = ref(checkIn.storageAvailable)
const backendStatus = ref('Checking backend…')
const returnToCompletion = ref(false)
const current = shallowRef(null)
const moodSaveState = ref('')
const navigationNote = ref('')
let moodRequest = 0
let entryClock = 0

async function focusHeading() {
  await nextTick()
  Array.from(document.querySelectorAll('main h1')).find(heading => heading.getClientRects().length)?.focus()
}
function dismissMood(mood = 'skipped') {
  const day = localDateKey()
  checkIn.dismiss()
  storageAvailable.value = checkIn.storageAvailable
  moodOpen.value = false
  focusHeading()
  const request = ++moodRequest
  moodSaveState.value = 'Check-in saving…'
  activityAPI.saveMood(day, mood).then(
    () => { if (request === moodRequest) moodSaveState.value = 'Check-in saved.' },
    () => { if (request === moodRequest) moodSaveState.value = 'Check-in not saved. You can keep using Pause.' },
  )
}
function endExercise(status) {
  const session = current.value
  const activeTiming = screen.value === 'breathing' ? breathingScreen.value?.stop() : null
  if (!session || session.terminal || !session.recorder) return
  const duration = Math.round(Math.max(0, performance.now() - session.startClock)) / 1000
  const endedAt = new Date(Date.parse(session.startedAt) + duration * 1000).toISOString()
  session.terminal = status
  session.duration = duration
  session.recorder.finish({ status, ended_at: endedAt, duration_seconds: duration,
    ...(session.exercise === 'breathing' && activeTiming ? activeTiming : {}),
  })
}
function chooseFeedback(value) {
  const session = current.value
  if (session?.terminal !== 'completed') return
  session.feedback = value
  const ready = session.recorder.feedback(value)
  session.responder.select(value, ready)
}
function goHome() {
  conversationScreen.value?.endVoice()
  if (screen.value === 'breathing' || screen.value === 'grounding') endExercise('exited')
  if (screen.value === 'completion' && !current.value?.feedback) chooseFeedback('skipped')
  current.value?.responder?.cancel()
  screen.value = 'home'
  checkDay()
  focusHeading()
}
function openConversation() {
  screen.value = 'conversation'
  focusHeading()
}
function choose(exercise) {
  conversationScreen.value?.endVoice()
  current.value = reactive({ id: crypto.randomUUID(), exercise, recorder: null, terminal: null, feedback: '', saveState: '', startClock: null, startedAt: null, duration: null, responder: null, response: { status: 'idle', text: '', label: '' } })
  entryClock = performance.now()
  navigationNote.value = ''
  screen.value = exercise
  focusHeading()
}
function instructionStarted({ startClock, startedAt }) {
  const session = current.value
  if (!session || session.recorder) return
  session.startClock = startClock
  session.startedAt = startedAt
  session.recorder = createSessionRecorder({
    api: activityAPI,
    payload: { id: session.id, exercise_type: session.exercise === 'breathing' ? 'paced_breathing' : 'grounding_54321', started_at: startedAt, entry_duration_seconds: Math.round(Math.max(0, startClock - entryClock)) / 1000 },
    onState: value => { session.saveState = value },
  })
  session.responder = createFeedbackResponder({
    api: activityAPI, sessionId: session.id,
    localDate: localDateKey,
    exerciseType: session.exercise === 'breathing' ? 'paced_breathing' : 'grounding_54321',
    onState: value => { session.response = value },
  })
  session.recorder.start()
}
function complete() {
  if (!['breathing', 'grounding'].includes(screen.value)) return
  endExercise('completed')
  screen.value = 'completion'
  focusHeading()
}
function openSupport() {
  conversationScreen.value?.endVoice()
  if (moodOpen.value) dismissMood()
  returnToCompletion.value = screen.value === 'completion'
  if (screen.value === 'breathing' || screen.value === 'grounding') endExercise('exited')
  screen.value = 'crisis'
  focusHeading()
}
function closeSupport() {
  screen.value = returnToCompletion.value ? 'completion' : 'home'
  if (screen.value === 'home') checkDay()
  focusHeading()
}
function checkDay() {
  if (document.visibilityState === 'hidden') return
  const dismissed = checkIn.isDismissed()
  storageAvailable.value = checkIn.storageAvailable
  if (dismissed && moodOpen.value) {
    moodOpen.value = false
    focusHeading()
  } else if (!dismissed && screen.value === 'home') moodOpen.value = true
}
function visibilityChanged() {
  if (document.visibilityState === 'hidden' && screen.value === 'breathing') {
    breathingScreen.value?.pause()
  } else checkDay()
}
function leavingPage() {
  if (screen.value === 'breathing' || screen.value === 'grounding') endExercise('exited')
}
onMounted(async () => {
  window.addEventListener('focus', checkDay)
  window.addEventListener('storage', checkDay)
  window.addEventListener('pagehide', leavingPage)
  document.addEventListener('visibilitychange', visibilityChanged)
  try {
    await getHealth()
    backendStatus.value = 'Backend ready'
  } catch {
    backendStatus.value = 'Backend unavailable · navigation still works'
  }
})
onUnmounted(() => {
  window.removeEventListener('focus', checkDay)
  window.removeEventListener('storage', checkDay)
  window.removeEventListener('pagehide', leavingPage)
  document.removeEventListener('visibilitychange', visibilityChanged)
})
</script>
<template>
  <div class="app-shell">
    <SafetyHeader :active="screen === 'crisis'" @support="openSupport" />
    <main>
      <HomeScreen v-if="screen === 'home'" @choose="choose" @conversation="openConversation" />
      <ConversationScreen v-else-if="screen === 'conversation'" ref="conversationScreen" @home="goHome" />
      <BreathingScreen v-else-if="screen === 'breathing'" ref="breathingScreen" @started="instructionStarted" @exit="goHome" @complete="complete" />
      <GroundingScreen v-else-if="screen === 'grounding'" @started="instructionStarted" @exit="goHome" @finish="complete" />
      <CompletionScreen v-if="screen === 'completion'" :feedback="current?.feedback" :save-state="current?.saveState" :response="current?.response" @feedback="chooseFeedback" @home="goHome" />
      <CrisisScreen v-if="screen === 'crisis'" :return-to-completion="returnToCompletion" @return="closeSupport" />
    </main>
    <footer class="screen-footer">
      <p v-if="navigationNote" class="storage-note" role="status">{{ navigationNote }}</p>
      <p v-if="current?.saveState && screen !== 'completion'" class="save-status" role="status">{{ current.saveState }}</p>
      <p v-if="moodSaveState" class="save-status" role="status">{{ moodSaveState }}</p>
      <p class="prototype">Coursework prototype — not a mental health support service.</p>
      <p class="connection-status" role="status">{{ backendStatus }}</p>
    </footer>
    <MoodDialog v-if="moodOpen" :storage-available="storageAvailable" @dismiss="dismissMood" @support="openSupport" />
  </div>
</template>
