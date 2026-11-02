<script setup>
import { nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { createHistoryReader, exerciseNames, sessionStatuses, feedbackNames, conversationType, formatDate, formatDuration } from '../history.js'
const props=defineProps({api:{type:Object,required:true}})
defineEmits(['home'])
const heading=ref(null)
const state=ref({listStatus:'loading',sessions:[],conversations:[],selected:null,detailStatus:'idle',conversation:null})
const reader=createHistoryReader({api:props.api,onState:value=>{state.value=value}})
watch(()=>state.value.selected,async()=>{await nextTick();heading.value?.focus()})
onMounted(()=>reader.load())
onBeforeUnmount(()=>reader.dispose())
</script>
<template>
  <section class="history-content" aria-labelledby="screen-heading" :data-conversation-id="state.selected || undefined">
    <p class="eyebrow">Saved activity</p>
    <h1 ref="heading" id="screen-heading" tabindex="-1">{{ state.selected ? 'Saved conversation' : 'History' }}</h1>
    <template v-if="!state.selected">
      <p v-if="state.listStatus === 'loading'" role="status" class="muted">Loading history…</p>
      <div v-else-if="state.listStatus === 'error'" role="status" class="history-notice">
        <p>History is unavailable right now.</p><button type="button" class="secondary wide" @click="reader.load()">Try again</button>
      </div>
      <template v-else-if="state.listStatus === 'ready'">
        <section aria-labelledby="exercise-history-heading" class="history-section">
          <h2 id="exercise-history-heading">Recent exercises</h2>
          <p v-if="!state.sessions.length" class="muted">No saved exercises yet.</p>
          <ul v-else class="history-list">
            <li v-for="session in state.sessions" :key="session.id" :data-session-id="session.id" class="history-card">
              <strong>{{ exerciseNames[session.exercise_type] }}</strong>
              <span class="history-status">{{ sessionStatuses[session.status] }}</span>
              <time :datetime="session.started_at">{{ formatDate(session.started_at) }}</time>
              <p v-if="session.active_duration_seconds != null">Active {{ formatDuration(session.active_duration_seconds) }} · Total {{ formatDuration(session.duration_seconds) }}</p>
              <p v-else>Duration: {{ formatDuration(session.duration_seconds) }}</p>
              <p v-if="session.feedback">Feedback: {{ feedbackNames[session.feedback] }}</p>
            </li>
          </ul>
        </section>
        <section aria-labelledby="conversation-history-heading" class="history-section">
          <h2 id="conversation-history-heading">Recent conversations</h2>
          <p class="history-caption">Saved text only. Voice conversations aren’t saved.</p>
          <p v-if="!state.conversations.length" class="muted">No saved conversations yet.</p>
          <ul v-else class="history-list">
            <li v-for="conversation in state.conversations" :key="conversation.id">
              <button type="button" class="history-card history-open" @click="reader.open(conversation.id)">
                <strong>{{ conversationType(conversation.kind) }}</strong>
                <time :datetime="conversation.created_at">{{ formatDate(conversation.created_at) }}</time>
                <p>{{ conversation.preview }}</p><span class="history-open-label">Open conversation →</span>
              </button>
            </li>
          </ul>
        </section>
        <p class="history-caption">Up to 20 recent records in each section.</p>
      </template>
    </template>
    <template v-else>
      <p v-if="state.detailStatus === 'loading'" role="status" class="muted">Loading conversation…</p>
      <div v-else-if="state.detailStatus === 'error'" role="status" class="history-notice">
        <p>This conversation is unavailable.</p><button type="button" class="secondary wide" @click="reader.open(state.selected)">Try again</button>
      </div>
      <template v-else-if="state.detailStatus === 'ready'">
        <p class="history-caption">{{ conversationType(state.conversation.kind) }} · {{ state.conversation.provider_mode === 'mock' ? 'Demo · mock provider' : 'Live-model record' }}</p>
        <p v-if="state.conversation.status === 'failed'" role="status" class="history-caption">No assistant reply was saved.</p>
        <p v-else-if="state.conversation.status === 'pending'" role="status" class="history-caption">Response pending.</p>
        <ol class="history-list history-messages" aria-label="Saved messages in chronological order">
          <li v-for="message in state.conversation.messages" :key="message.id" :data-message-id="message.id" class="history-card">
            <strong>{{ message.role === 'user' ? 'You' : 'Assistant' }}</strong>
            <time :datetime="message.created_at">{{ formatDate(message.created_at) }}</time>
            <p>{{ message.content }}</p>
          </li>
        </ol>
      </template>
      <button type="button" class="secondary wide history-back" @click="reader.back()">Back to History</button>
    </template>
    <button type="button" class="secondary wide history-home" @click="$emit('home')">Return Home</button>
  </section>
</template>
