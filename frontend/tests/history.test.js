import {test} from 'node:test'
import assert from 'node:assert/strict'
import {createHistoryReader,createRecentExerciseReader,formatDuration,formatDate} from '../src/history.js'
import {createActivityAPI} from '../src/api.js'
const id='73d5dab3-87a0-42cc-85bc-079bedc1f178',other='bc3ea124-f6c8-490a-a828-6373c9f558c9'
const empty=()=>({sessions:[],conversations:[],recent_completed_exercise:null})
const result=()=>({...empty(),sessions:[{id,exercise_type:'paced_breathing',status:'completed',duration_seconds:95.881,active_duration_seconds:66.147}],conversations:[{id,kind:'feedback',preview:'Saved feedback after Paced Breathing.'}]})
const conversation=value=>({id:value,messages:[{id:'u',ordinal:1,role:'user',content:'Fictional choice.'},{id:'a',ordinal:2,role:'assistant',content:'Fictional reply.'}]})
const deferred=()=>{let resolve,reject;const promise=new Promise((yes,no)=>{resolve=yes;reject=no});return{promise,resolve,reject}}
const flush=async()=>{for(let n=0;n<10;n++)await Promise.resolve()}
function setup(api){const states=[];return {states,reader:createHistoryReader({api,onState:s=>states.push(s)})}}
test('history API uses scoped read-only GETs, bounded list parameter, no cache and no provider request',async()=>{
 const calls=[];const api=createActivityAPI('fictional-owner',async(url,options)=>{calls.push({url,...options});return{ok:true,json:async()=>empty()}})
 await api.history(20,new AbortController().signal);await api.conversation(id,new AbortController().signal)
 assert.deepEqual(calls.map(c=>c.url),['/api/history?limit=20','/api/conversations/'+id])
 for(const call of calls){assert.equal(call.method,'GET');assert.equal(call.cache,'no-store');assert.equal(call.headers['X-App-ID'],'fictional-owner');assert.equal('body' in call,false);assert.ok(call.signal)}
})
test('empty and saved lists have distinct ready states; details retain saved chronological order',async()=>{
 let list=empty();const s=setup({history:async()=>list,conversation:async value=>conversation(value)})
 await s.reader.load();assert.equal(s.states.at(-1).listStatus,'ready');assert.deepEqual(s.states.at(-1).sessions,[])
 list=result();await s.reader.load();assert.equal(s.states.at(-1).sessions[0].active_duration_seconds,66.147)
 await s.reader.open(id);assert.equal(s.states.at(-1).detailStatus,'ready');assert.deepEqual(s.states.at(-1).conversation.messages.map(m=>m.role),['user','assistant'])
 s.reader.back();assert.equal(s.states.at(-1).selected,null);assert.equal(s.states.at(-1).sessions.length,1)
})
test('backend failure, missing IDs and malformed data yield neutral retriable states',async()=>{
 const s=setup({history:async()=>{throw Error('private database detail')},conversation:async()=>{throw Error('404')}})
 await s.reader.load();assert.equal(s.states.at(-1).listStatus,'error');assert.doesNotMatch(JSON.stringify(s.states),/private/)
 await s.reader.open(id);assert.equal(s.states.at(-1).detailStatus,'error')
 const bad=setup({history:async()=>({sessions:[],conversations:[]}),conversation:async()=>({id:other,messages:[]})})
 await bad.reader.load();assert.equal(bad.states.at(-1).listStatus,'error')
 await bad.reader.open(id);assert.equal(bad.states.at(-1).detailStatus,'error')
})
test('invalid conversation IDs never issue a read request',async()=>{
 let calls=0;const s=setup({conversation:async()=>calls++})
 for(const value of ['invalid','../../credentials']){await s.reader.open(value);assert.equal(s.states.at(-1).detailStatus,'error')}
 assert.equal(calls,0)
})
test('Home/support/unmount disposal aborts pending history and ignores late reads',async()=>{
 const pending=deferred();let signal;const s=setup({history:(_,value)=>{signal=value;return pending.promise}})
 const request=s.reader.load();s.reader.dispose();const count=s.states.length
 assert.equal(signal.aborted,true);pending.resolve(result());await request;assert.equal(s.states.length,count)
})
test('newer conversation selection and Back ignore old results without hiding saved lists',async()=>{
 const old=deferred(),latest=deferred();const signals=[]
 const s=setup({history:async()=>result(),conversation:(value,signal)=>{signals.push(signal);return value===id?old.promise:latest.promise}})
 await s.reader.load();const a=s.reader.open(id),b=s.reader.open(other)
 assert.equal(signals[0].aborted,true);latest.resolve(conversation(other));await b;old.resolve(conversation(id));await a
 assert.equal(s.states.at(-1).conversation.id,other);s.reader.back();assert.equal(signals[1].aborted,true);assert.equal(s.states.at(-1).selected,null)
})
test('personalization waits for writes, uses only returned completion, and can be absent',async()=>{
 const saved=deferred(),values=[],calls=[]
 const reader=createRecentExerciseReader({api:{history:async limit=>{calls.push(limit);return {...empty(),recent_completed_exercise:'grounding_54321'}}},onValue:v=>values.push(v)})
 const request=reader.load(saved.promise);await flush();assert.deepEqual(calls,[]);assert.equal(values.at(-1),null)
 saved.resolve(true);await request;assert.deepEqual(calls,[1]);assert.equal(values.at(-1),'grounding_54321')
 const unavailable=createRecentExerciseReader({api:{history:async()=>{throw Error('offline')}},onValue:v=>values.push(v)})
 await unavailable.load();assert.equal(values.at(-1),null)
})
test('stale personalization cannot appear after departure or replace a newer read',async()=>{
 const pending=deferred();let calls=0;const values=[]
 const reader=createRecentExerciseReader({api:{history:async()=>++calls===1?pending.promise:{...empty(),recent_completed_exercise:'paced_breathing'}},onValue:v=>values.push(v)})
 const old=reader.load();await flush();await reader.load();pending.resolve({...empty(),recent_completed_exercise:'grounding_54321'});await old
 assert.equal(values.at(-1),'paced_breathing');const saved=deferred();const late=reader.load(saved.promise);reader.cancel();saved.resolve(true);await late;assert.equal(values.at(-1),null)
})
test('durations distinguish missing, zero, short exits and separate active/wall measurements',()=>{
 assert.equal(formatDuration(null),'Not recorded');assert.equal(formatDuration(0),'0s');assert.equal(formatDuration(1.214),'1.2s')
 assert.equal(formatDuration(66.147),'1m 6.1s');assert.equal(formatDuration(95.881),'1m 35.9s');assert.equal(formatDuration(59.999),'1m 0s')
 assert.equal(formatDate('invalid'),'Date unavailable')
})
