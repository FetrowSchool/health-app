import { test } from 'node:test'
import assert from 'node:assert/strict'
import { GROUNDING_STEPS, createGroundingProgress, toggleNoticed } from '../src/grounding.js'
import { feedbackMessage, createFeedbackResponder } from '../src/feedbackResponse.js'

test('reviewed senses/counts/instructions are fixed and intended timing is70 seconds',()=>{
  assert.deepEqual(GROUNDING_STEPS.map(s=>[s.sense,s.count,s.instruction]),[
    ['Sight',5,'Notice 5 things you can see.'],['Touch',4,'Notice 4 things you can feel.'],
    ['Hearing',3,'Notice 3 things you can hear.'],['Smell',2,'Notice 2 things you can smell.'],['Taste',1,'Notice 1 thing you can taste.']])
  assert.equal(GROUNDING_STEPS.reduce((n,s)=>n+s.seconds,0),70)
  assert.equal(Object.isFrozen(GROUNDING_STEPS[0]),true)
})
test('noticing can be undone and earlier-step progress survives other-step changes',()=>{
  const progress=createGroundingProgress()
  assert.deepEqual(progress.map(p=>p.length),[5,4,3,2,1])
  toggleNoticed(progress,0,2);toggleNoticed(progress,1,0)
  assert.equal(progress[0][2],true)
  toggleNoticed(progress,0,2);assert.equal(progress[0][2],false)
  assert.equal(progress[1][0],true)
  toggleNoticed(progress,5,0);toggleNoticed(progress,0,9)
  assert.deepEqual(progress.map(p=>p.length),[5,4,3,2,1])
  assert.equal(createGroundingProgress()[1][0],false) // restart clears current-exercise taps
})
test('Grounding feedback uses correct context and duplicate-safe response controller',async()=>{
  const calls=[],states=[]
  const responder=createFeedbackResponder({sessionId:'fictional-grounding',exerciseType:'grounding_54321',newId:()=> 'fictional-request',onState:s=>states.push(s),api:{feedbackResponse:async body=>{
    calls.push(body);return {session_id:body.session_id,feedback:body.feedback,status:'succeeded',saved:true,provider_mode:'mock',messages:[{role:'assistant',ordinal:2,content:'Feedback noted. You can return home whenever you choose.'}]}
  }}})
  await responder.select('helpful');await responder.select('helpful')
  assert.equal(calls.length,1);assert.equal(calls[0].exercise_type,'grounding_54321')
  assert.equal(calls[0].user_message,feedbackMessage('grounding_54321','helpful'))
  assert.equal(states.at(-1).label,'Demo response · mock provider')
})
