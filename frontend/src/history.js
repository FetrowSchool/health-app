export const exerciseNames = Object.freeze({paced_breathing:'Paced Breathing',grounding_54321:'5-4-3-2-1 Grounding',stop:'STOP (earlier exercise)'})
export const sessionStatuses = Object.freeze({completed:'Completed',exited:'Exited',started:'Started · unfinished'})
export const feedbackNames = Object.freeze({helpful:'Helpful',not_helpful:'Not Helpful',skipped:'Skipped'})
export const conversationType = kind => kind === 'recommendation' ? 'Earlier exercise suggestion' : 'Exercise feedback'
export const isConversationId = id => typeof id === 'string' && /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(id)
export function formatDuration(seconds) {
  if (seconds == null || !Number.isFinite(seconds) || seconds < 0) return 'Not recorded'
  const tenths=Math.round(seconds*10),minutes=Math.floor(tenths/600),remainder=(tenths%600)/10
  return minutes ? `${minutes}m ${remainder}s` : `${remainder}s`
}
export function formatDate(value) {
  const date=new Date(value)
  return Number.isNaN(date.valueOf()) ? 'Date unavailable' : new Intl.DateTimeFormat(undefined,{dateStyle:'medium',timeStyle:'short'}).format(date)
}
function historyResult(value) {
  if (!Array.isArray(value?.sessions) || !Array.isArray(value?.conversations)
      || value.sessions.length>50 || value.conversations.length>50
      || ![null,'paced_breathing','grounding_54321'].includes(value.recent_completed_exercise)) throw Error('Invalid history')
  for (const row of value.sessions) if (!isConversationId(row.id) || !exerciseNames[row.exercise_type] || !sessionStatuses[row.status]) throw Error('Invalid session')
  for (const row of value.conversations) if (!isConversationId(row.id) || !['feedback','recommendation'].includes(row.kind)
      || typeof row.preview!=='string' || row.preview.length>160) throw Error('Invalid conversation')
  return value
}
export function createHistoryReader({api,onState}) {
  let state={listStatus:'idle',sessions:[],conversations:[],selected:null,detailStatus:'idle',conversation:null}
  let listRequest=0,detailRequest=0,listAbort,detailAbort,disposed=false
  const update = patch => { if (!disposed) { state={...state,...patch};onState(state) } }
  const back = () => { detailRequest++;detailAbort?.abort();update({selected:null,detailStatus:'idle',conversation:null}) }
  return {
    async load() {
      if (disposed) return
      const version=++listRequest;listAbort?.abort();listAbort=new AbortController();back()
      update({listStatus:'loading',sessions:[],conversations:[]})
      try {
        const result=historyResult(await api.history(20,listAbort.signal))
        if (!disposed && version===listRequest) update({listStatus:'ready',sessions:result.sessions,conversations:result.conversations})
      } catch { if (!disposed && version===listRequest) update({listStatus:'error'}) }
    },
    async open(id) {
      if (disposed) return
      const version=++detailRequest;detailAbort?.abort();detailAbort=new AbortController()
      update({selected:id,detailStatus:'loading',conversation:null})
      try {
        if (!isConversationId(id)) throw Error('Invalid ID')
        const value=await api.conversation(id,detailAbort.signal)
        if (value?.id!==id || !Array.isArray(value.messages) || value.messages.some(m=>!['user','assistant'].includes(m.role)
            || typeof m.content!=='string' || !Number.isInteger(m.ordinal))) throw Error('Invalid conversation')
        if (!disposed && version===detailRequest) update({detailStatus:'ready',conversation:value})
      } catch { if (!disposed && version===detailRequest) update({detailStatus:'error'}) }
    },
    back,
    dispose() { disposed=true;listRequest++;detailRequest++;listAbort?.abort();detailAbort?.abort() },
  }
}
// One optional read on each Home entry, after pending session writes settle.
// No preferences, mood interpretation, generated recommendation or provider call.
export function createRecentExerciseReader({api,onValue}) {
  let revision=0,abort
  const cancel=()=>{revision++;abort?.abort()}
  return {
    async load(ready=Promise.resolve()) {
      cancel();const version=revision;abort=new AbortController();const signal=abort.signal;onValue(null)
      try {
        await ready
        if (version!==revision) return
        const value=historyResult(await api.history(1,signal)).recent_completed_exercise
        if (version===revision) onValue(value)
      } catch { /* Optional personalization stays absent on a read failure. */ }
    },cancel,
  }
}
