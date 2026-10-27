import { test } from 'node:test'
import assert from 'node:assert/strict'
import { createBreathingControl } from '../src/breathingInteraction.js'
import { createBreathingTimer } from '../src/exerciseTiming.js'
import { createSessionRecorder } from '../src/sessionRecorder.js'
function setup() {
 let now=0, frame, starts=0
 const states=[]
 const timer=createBreathingTimer({now:()=>now,schedule:fn=>{frame=fn;return 1},cancel:()=>{},onStarted:()=>starts++,onUpdate:s=>states.push(s)})
 return {timer,control:createBreathingControl(timer),states,advance(ms){now+=ms;frame?.()},get starts(){return starts}}
}
test('opening is idle; primary hold starts once and release/resume preserves active progress',()=>{
 const s=setup();s.advance(5000);assert.equal(s.starts,0);assert.equal(s.timer.snapshot().activeMs,0)
 s.control.pointerDown(1);s.advance(2300);s.control.pointerUp(1)
 assert.equal(s.timer.snapshot().activeMs,2300);assert.equal(s.timer.snapshot().running,false)
 s.advance(10000);assert.equal(s.timer.snapshot().activeMs,2300)
 s.control.pointerDown(2);s.advance(2100);s.control.pointerUp(2)
 assert.equal(s.timer.snapshot().phase,'out');assert.equal(s.timer.snapshot().activeMs,4400)
 assert.equal(s.starts,1);assert.equal(s.timer.snapshot().wallMs,14400)
})
test('cancellation/lost focus clears input ownership and late pointer/keyboard events cannot resume',()=>{
 const s=setup();s.control.pointerDown(7);s.advance(1234);s.control.pause();s.advance(5000)
 s.control.pointerUp(7);s.control.keyUp(' ');assert.equal(s.timer.snapshot().activeMs,1234)
 assert.equal(s.timer.snapshot().running,false)
 s.control.keyDown('Enter');s.advance(1000);s.control.keyUp('Enter');assert.equal(s.timer.snapshot().activeMs,2234)
})
test('Space/Enter and accessible Start/Pause work without repeats or duplicate starts',()=>{
 const s=setup();s.control.keyDown(' ',false);s.control.keyDown(' ',true);s.advance(4000);s.control.keyUp(' ')
 assert.equal(s.timer.snapshot().phase,'out');assert.equal(s.starts,1)
 s.control.toggle();s.advance(6000);s.control.toggle();assert.equal(s.timer.snapshot().completedCycles,1)
 s.advance(5000);assert.equal(s.timer.snapshot().activeMs,10000)
 s.control.keyDown('Enter');s.advance(1000);s.control.keyUp('Enter');assert.equal(s.starts,1)
})
test('Pause intent survives focus loss before an accessible button click',()=>{
 const s=setup();s.control.pointerDown(1);s.advance(1500)
 const wasRunning=s.timer.snapshot().running;s.control.pause();s.control.toggle(wasRunning)
 assert.equal(s.timer.snapshot().running,false);assert.equal(s.timer.snapshot().activeMs,1500)
})
test('planned completion is a notice, optional cycles continue, explicit stop is terminal',()=>{
 const s=setup();s.control.pointerDown(1);s.advance(60000)
 assert.equal(s.timer.snapshot().plannedComplete,true);assert.equal(s.timer.snapshot().running,true)
 s.advance(15000);s.control.stop();assert.deepEqual(s.timer.summary(),{active_duration_seconds:75,optional_continuation_seconds:15,active_completed_cycles:7})
 s.control.toggle();s.control.pointerDown(2);s.advance(10000);assert.equal(s.timer.snapshot().activeMs,75000)
})
test('first interaction, multiple pauses, early Finish and feedback create only one saved session',async()=>{
 let now=0, frame;const calls=[]
 const recorder=createSessionRecorder({api:{startSession:async()=>calls.push('start'),endSession:async(id,body)=>calls.push(body),saveFeedback:async()=>calls.push('feedback')},payload:{id:'fictional'}})
 const timer=createBreathingTimer({now:()=>now,schedule:fn=>{frame=fn;return 1},cancel:()=>{},onUpdate:()=>{},onStarted:()=>recorder.start()})
 const control=createBreathingControl(timer);assert.deepEqual(calls,[])
 control.pointerDown(1);now=1000;frame();control.pointerUp(1);now=9000;control.toggle();now=10000;control.stop()
 await recorder.finish({status:'completed',duration_seconds:10,...timer.summary()});await recorder.feedback('skipped')
 assert.equal(calls.filter(x=>x==='start').length,1);assert.equal(calls[1].active_duration_seconds,2)
 assert.equal(calls[1].duration_seconds,10);assert.equal(calls[1].status,'completed');assert.equal(calls[2],'feedback')
})
