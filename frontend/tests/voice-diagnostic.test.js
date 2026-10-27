import { test } from 'node:test'
import assert from 'node:assert/strict'
import { createDiagnosticAPI, probeMicrophone } from '../src/voiceDiagnostic.js'

test('microphone-only probe requests no API and stops every granted track', async () => {
 let stopped=0
 const result=await probeMicrophone({getUserMedia:async constraints=>{assert.deepEqual(constraints,{audio:true,video:false});return {getAudioTracks:()=>[{}],getTracks:()=>[{stop(){stopped++}},{stop(){stopped++}}]}}})
 assert.equal(stopped,2);assert.match(result,/granted/)
})
test('microphone-only failures are classified without private browser detail', async () => {
 for(const name of ['NotAllowedError','NotFoundError','NotReadableError','Error']){
  const result=await probeMicrophone({getUserMedia:async()=>{throw Object.assign(Error('PRIVATE'),{name})}})
  assert.doesNotMatch(result,/PRIVATE/);assert.match(result,/Microphone|microphone/)
 }
})
test('diagnostic API targets only isolated FastAPI with SDP, no browser model or key', async () => {
 let request
 const api=createDiagnosticAPI(async(url,options)=>{request={url,options};return {ok:true,json:async()=>({session_id:'opaque-test',sdp:'v=0\r\nanswer',duration_seconds:30})}})
 await api.createSession('v=0\r\noffer')
 assert.equal(request.url,'http://127.0.0.1:8001/api/voice/sessions')
 assert.deepEqual(JSON.parse(request.options.body),{sdp:'v=0\r\noffer'})
 assert.equal(request.options.headers.Authorization,undefined)
})
