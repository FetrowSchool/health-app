import { test } from 'node:test'
import assert from 'node:assert/strict'
import { breathingState, createBreathingTimer, PLANNED_DURATION_MS } from '../src/exerciseTiming.js'
import { createSessionRecorder } from '../src/sessionRecorder.js'
import { applicationIdentity } from '../src/composables/appIdentity.js'
import { createActivityAPI } from '../src/api.js'
const payload = { id:'fictional-session', exercise_type:'stop', started_at:'2026-10-19T12:00:00.000Z', entry_duration_seconds:0.01 }
const terminal = { status:'completed', ended_at:'2026-10-19T12:01:00.000Z', duration_seconds:60 }

test('4-second inhale / 6-second exhale pattern continues beyond the six planned cycles', () => {
  assert.equal(PLANNED_DURATION_MS,60000)
  for(let cycle=0;cycle<10;cycle++) for(let second=0;second<10;second++){
   const state=breathingState(cycle*10000+second*1000)
   assert.equal(state.cycle,cycle+1);assert.equal(state.phase,second<4?'in':'out')
   assert.equal(state.seconds,second<4?4-second:10-second)
   assert.equal(state.plannedComplete,cycle>=6)
  }
  for(const [ms,expansion] of [[0,0],[2000,.5],[4000,1],[7000,.5],[10000,0]])assert.equal(breathingState(ms).expansion,expansion)
})
test('delayed frames use elapsed active time without drift, and pauses/stop invalidate late callbacks',()=>{
 let time=123, callback,starts=0;const states=[],canceled=[]
 const timer=createBreathingTimer({now:()=>time,schedule:fn=>{callback=fn;return 42},cancel:id=>canceled.push(id),onUpdate:s=>states.push(s),onStarted:()=>starts++})
 timer.resume();time=14623;callback();assert.equal(states.at(-1).activeMs,14500)
 assert.equal(states.at(-1).phase,'out');const late=callback;timer.pause();time+=15000;late()
 assert.equal(timer.snapshot().activeMs,14500);timer.resume();time+=500;callback();assert.equal(timer.snapshot().activeMs,15000)
 timer.stop();time+=100000;callback();assert.equal(timer.snapshot().activeMs,15000);assert.equal(starts,1);assert.ok(canceled.length)
})
test('exit before start response does not block and updates only the same session', async () => {
  let resolveStart
  const calls=[]
  const api={startSession:p=>{calls.push(['start',p.id]);return new Promise(resolve=>{resolveStart=resolve})},endSession:async(id,body)=>calls.push(['end',id,body.status])}
  const recorder=createSessionRecorder({api,payload})
  recorder.start();await Promise.resolve()
  const end=recorder.finish({...terminal,status:'exited'})
  assert.equal(calls.length,1)
  recorder.finish(terminal)
  resolveStart({});await end
  assert.deepEqual(calls,[['start',payload.id],['end',payload.id,'exited']])
})
test('rapid feedback serializes without duplicate starts/ends and preserves last choice', async () => {
  const calls=[]
  const api={startSession:async p=>calls.push(['start',p.id]),endSession:async id=>calls.push(['end',id]),saveFeedback:async(id,value)=>calls.push(['feedback',id,value])}
  const recorder=createSessionRecorder({api,payload})
  recorder.start();recorder.finish(terminal);recorder.feedback('helpful');recorder.feedback('not_helpful');await recorder.settled()
  assert.deepEqual(calls,[['start',payload.id],['end',payload.id],['feedback',payload.id,'helpful'],['feedback',payload.id,'not_helpful']])
})
test('failure stays unsaved without blocking; later choice can recover the same session', async () => {
  let fail=true
  const states=[],calls=[]
  const api={startSession:async()=>{if(fail)throw Error('offline')},endSession:async id=>calls.push(id),saveFeedback:async()=>{}}
  const recorder=createSessionRecorder({api,payload,onState:s=>states.push(s)})
  await recorder.start();await recorder.finish(terminal);assert.match(states.at(-1),/not saved/)
  fail=false;await recorder.feedback('skipped')
  assert.equal(states.at(-1),'Feedback saved.');assert.deepEqual(calls,[payload.id])
})
test('old acknowledgment cannot hide a pending newer feedback save', async () => {
  let release
  const states=[]
  const api={startSession:async()=>{},endSession:async()=>{},saveFeedback:()=>new Promise(resolve=>{release=resolve})}
  const recorder=createSessionRecorder({api,payload,onState:s=>states.push(s)})
  recorder.start();recorder.finish(terminal);const pending=recorder.feedback('helpful')
  for(let i=0;i<12;i++)await Promise.resolve()
  assert.equal(states.at(-1),'Feedback saving…');release({});await pending
  assert.equal(states.at(-1),'Feedback saved.')
})
test('pseudonymous identity survives reload; blocked storage supports this visit', () => {
  const entries=new Map(),storage={getItem:key=>entries.get(key),setItem:(key,value)=>entries.set(key,value)}
  const id='36fabd92-2543-4569-84c5-c40744e25a83'
  assert.equal(applicationIdentity(()=>storage,()=>id),id)
  assert.equal(applicationIdentity(()=>storage,()=>{throw Error('must reuse')}),id)
  assert.equal(applicationIdentity(()=>{throw Error('blocked')},()=>id),id)
})
test('activity API sends correct identity/method/body and bounded requests, rejects failures', async () => {
  const calls=[]
  const api=createActivityAPI('fictional-app',async(url,options)=>{calls.push({url,...options});return {ok:true,json:async()=>({})}})
  await api.startSession(payload);await api.endSession(payload.id,terminal);await api.saveFeedback(payload.id,'helpful');await api.saveMood('2026-10-19','skipped')
  assert.deepEqual(calls.map(c=>c.method),['POST','PATCH','PUT','PUT']);assert.equal(calls[0].headers['X-App-ID'],'fictional-app')
  assert.ok(calls.every(c=>c.signal&&c.keepalive));assert.deepEqual(JSON.parse(calls.at(-1).body),{mood:'skipped'})
  await assert.rejects(()=>createActivityAPI('id',async()=>({ok:false})).saveMood('2026-10-19','calm'))
})
