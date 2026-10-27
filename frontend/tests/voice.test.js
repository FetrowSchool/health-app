import { test } from 'node:test'
import assert from 'node:assert/strict'
import { createVoiceSession, CLOSE_WAIT_MS } from '../src/voiceSession.js'
import { createVoiceAPI } from '../src/api.js'
import { bindVoiceLifecycle } from '../src/voiceLifecycle.js'
import { createFeedbackResponder } from '../src/feedbackResponse.js'

const deferred = () => { let resolve, reject; const promise = new Promise((yes, no) => { resolve = yes; reject = no }); return { promise, resolve, reject } }
const flush = async () => { for (let i = 0; i < 20; i++) await Promise.resolve() }
const event = (target, type, fields = {}) => target.dispatchEvent(Object.assign(new Event(type), fields))
class Clock {
  now = 0; next = 1; jobs = new Map()
  setTimeout = (fn, ms) => { const id = this.next++; this.jobs.set(id, { fn, time: this.now + ms }); return id }
  clearTimeout = id => this.jobs.delete(id)
  tick(ms) {
    const end = this.now + ms
    while (true) {
      const next = [...this.jobs.entries()].filter(([, j]) => j.time <= end).sort((a, b) => a[1].time - b[1].time)[0]
      if (!next) break
      this.jobs.delete(next[0]); this.now = next[1].time; next[1].fn()
    }
    this.now = end
  }
}
class Track extends EventTarget {
  kind = 'audio'; enabled = true; stopped = false
  stop() { this.stopped = true }
}
const stream = () => { const track = new Track(); return { track, getTracks: () => [track], getAudioTracks: () => [track] } }
class Channel extends EventTarget {
  readyState = 'open'; sent = []; closed = false
  send(value) { this.sent.push(JSON.parse(value)) }
  close() { this.closed = true; this.readyState = 'closed'; event(this, 'close') }
  message(data) { event(this, 'message', { data: JSON.stringify(data) }) }
}
function setup(options = {}) {
  const states = [], order = [], hangups = [], diagnostics = [], clock = new Clock(), remote = stream()
  let mic = stream(), channel = new Channel()
  let configCalls = 0, mediaCalls = 0, postCalls = 0, peerCalls = 0, submitted, signal, creationSignal
  class Peer extends EventTarget {
    iceGatheringState = options.waitForIce ? 'gathering' : 'complete'
    connectionState = 'new'; closed = false
    addTrack(track, input) { assert.equal(input, mic); order.push('track') }
    createDataChannel(label) { assert.equal(label, 'oai-events'); order.push('channel'); return channel }
    async createOffer() { order.push('offer'); return { type: 'offer', sdp: 'v=0\r\ninitial-offer' } }
    async setLocalDescription(offer) { order.push('local'); this.localDescription = { ...offer, sdp: 'v=0\r\nfinal-offer-with-ice' } }
    async setRemoteDescription(answer) { order.push('remote'); assert.deepEqual(answer, { type: 'answer', sdp: 'v=0\r\nfictional-answer' }); if (options.answer) await options.answer.promise }
    close() { this.closed = true; this.connectionState = 'closed'; event(this, 'connectionstatechange') }
  }
  let peer = new Peer()
  const audio = { srcObject: null, plays: 0, pauses: 0,
    play() { this.plays++; return options.play ? options.play(this.plays) : Promise.resolve() },
    pause() { this.pauses++ },
  }
  const api = {
    async closeSession(id) { hangups.push(id); if (options.hangup) return options.hangup(id) },
    async config(s) { configCalls++; signal = s; return options.config ? options.config(s) : { status: 'configured', duration_seconds: 60 } },
    async createSession(sdp, s) { postCalls++; submitted = sdp; creationSignal = s; order.push('post'); return options.post ? options.post(s) : { session_id: 'fictional-session', sdp: 'v=0\r\nfictional-answer', duration_seconds: 60 } },
  }
  const mediaDevices = { getUserMedia(constraints) { mediaCalls++; if (options.fresh && mediaCalls > 1) mic = stream(); assert.deepEqual(constraints, { audio: true, video: false }); return options.media ? options.media() : Promise.resolve(mic) } }
  const voice = createVoiceSession({ api, audio, mediaDevices, clock,
    onDiagnostic: item => { diagnostics.push(item); if (options.diagnosticThrows) throw Error('fictional diagnostic failure') },
    createPeer: () => { peerCalls++; if (options.fresh && peerCalls > 1) { peer = new Peer(); channel = new Channel() }; return peer }, remoteStream: () => remote, onState: state => states.push(state) })
  const started = () => channel.message({ type: 'session.started', session: { id: 'fictional-session' } })
  const attach = (withStream = true) => event(peer, 'track', { track: remote.track, streams: withStream ? [remote] : [] })
  const released = () => { assert.equal(mic.track.stopped, true); assert.equal(peer.closed, true); assert.equal(channel.closed, true); assert.equal(audio.srcObject, null); assert.equal(clock.jobs.size, 0) }
  return { voice, states, order, hangups, diagnostics, clock, get mic() { return mic }, remote, get channel() { return channel }, get peer() { return peer }, audio, started, attach, released,
    dispose: () => { voice.dispose(); clock.tick(CLOSE_WAIT_MS) }, creationSignal: () => creationSignal, last: () => states.at(-1), counts: () => ({ configCalls, mediaCalls, postCalls, peerCalls }), submitted: () => submitted, signal: () => signal }
}

test('nothing starts on mount; only explicit start connects, duplicates do not create another session', async () => {
  const s = setup()
  assert.deepEqual(s.counts(), { configCalls: 0, mediaCalls: 0, postCalls: 0, peerCalls: 0 })
  assert.equal(s.last().status, 'closed')
  const start = s.voice.start(); await s.voice.start(); await start
  assert.deepEqual(s.order, ['track', 'channel', 'offer', 'local', 'post', 'remote'])
  assert.equal(s.counts().postCalls, 1)
  assert.equal(s.last().status, 'connecting')
  event(s.channel, 'open'); s.peer.connectionState = 'connected'; event(s.peer, 'connectionstatechange')
  assert.equal(s.last().status, 'connecting')
  s.started(); assert.equal(s.last().status, 'active')
  s.dispose(); s.released()
})
test('ICE gathering finishes before FastAPI receives the final local SDP', async () => {
  const s = setup({ waitForIce: true }); const start = s.voice.start(); await flush()
  assert.equal(s.counts().postCalls, 0)
  s.peer.iceGatheringState = 'complete'; event(s.peer, 'icegatheringstatechange'); await start
  assert.equal(s.submitted(), 'v=0\r\nfinal-offer-with-ice')
  s.dispose(); s.released()
})
test('session.started during remote answer application cannot prematurely show Active', async () => {
  const answer = deferred(), s = setup({ answer }); const start = s.voice.start(); await flush()
  s.started(); assert.equal(s.last().status, 'connecting')
  answer.resolve(); await start; assert.equal(s.last().status, 'active')
  s.dispose(); s.released()
})
test('permission denial leaves text independent and allows an explicit new microphone attempt', async () => {
  let denied = true
  const s = setup({ media: () => denied ? Promise.reject(Object.assign(Error('private device detail'), { name: 'NotAllowedError' })) : Promise.resolve(s.mic) })
  await s.voice.start(); assert.equal(s.last().status, 'error'); assert.match(s.last().message, /permission/)
  assert.doesNotMatch(s.last().message, /private/); assert.equal(s.counts().postCalls, 0)
  denied = false; await s.voice.start(); s.started(); assert.equal(s.last().status, 'active')
  s.dispose(); s.released()
})
test('unconfigured or failed API does not request microphone permission', async () => {
  for (const config of [async () => ({ status: 'unconfigured' }), async () => { throw Error('private') }]) {
    const s = setup({ config }); await s.voice.start()
    assert.equal(s.last().status, 'error'); assert.equal(s.counts().mediaCalls, 0)
    assert.match(s.last().message, /text choices/); assert.doesNotMatch(s.last().message, /private/)
    assert.equal(s.clock.jobs.size, 0); s.dispose()
  }
})
test('mute only disables outgoing microphone tracks and can be reversed', async () => {
  const s = setup(); await s.voice.start(); s.started(); s.attach(); await flush()
  s.voice.toggleMute(); assert.equal(s.last().status, 'muted'); assert.equal(s.mic.track.enabled, false)
  assert.equal(s.remote.track.stopped, false); assert.equal(s.audio.srcObject, s.remote)
  s.voice.toggleMute(); assert.equal(s.last().status, 'active'); assert.equal(s.mic.track.enabled, true)
  s.dispose(); s.released(); assert.equal(s.remote.track.stopped, true)
})
test('blocked autoplay exposes a gesture retry that calls play immediately', async () => {
  const s = setup({ play: n => n === 1 ? Promise.reject(Error('autoplay')) : Promise.resolve() })
  await s.voice.start(); s.started(); s.attach(false); await flush()
  assert.equal(s.last().status, 'active'); assert.equal(s.last().audioBlocked, true)
  const retry = s.voice.enableAudio(); assert.equal(s.audio.plays, 2)
  await retry; assert.equal(s.last().audioBlocked, false)
  s.dispose(); s.released()
})
test('late failed autoplay cannot overwrite a newer successful gesture', async () => {
  const first = deferred(), s = setup({ play: n => n === 1 ? first.promise : Promise.resolve() })
  await s.voice.start(); s.started(); s.attach(); await s.voice.enableAudio()
  first.reject(Error('late autoplay failure')); await flush(); assert.equal(s.last().audioBlocked, false)
  s.dispose(); s.released()
})
test('End stops capture immediately, waits briefly, then releases resources and sends only session.close', async () => {
  const s = setup(); await s.voice.start(); s.started(); s.attach(); await flush()
  s.voice.stop(); assert.equal(s.last().status, 'closing')
  assert.equal(s.mic.track.stopped, true); assert.equal(s.remote.track.stopped, false); assert.equal(s.peer.closed, false)
  assert.deepEqual(s.channel.sent, [{ type: 'session.close' }]); assert.equal(s.signal().aborted, true)
  s.clock.tick(CLOSE_WAIT_MS); assert.equal(s.last().status, 'closed'); s.released()
  s.dispose()
})
test('cancel during permission releases late microphone tracks without creating a peer', async () => {
  const permission = deferred(), s = setup({ media: () => permission.promise })
  const start = s.voice.start(); await flush(); s.voice.stop(); s.clock.tick(CLOSE_WAIT_MS)
  permission.resolve(s.mic); await start
  assert.equal(s.mic.track.stopped, true); assert.equal(s.counts().peerCalls, 0); assert.equal(s.last().status, 'closed')
  assert.equal(s.clock.jobs.size, 0); s.dispose()
})
test('dispose keeps in-flight SDP observable and hangs up a late answer without reactivating', async () => {
  const post = deferred(), s = setup({ post: () => post.promise }); const start = s.voice.start(); await flush()
  s.dispose(); const count = s.states.length; assert.equal(s.signal().aborted, true)
  post.resolve({ session_id: 'fictional-session', sdp: 'v=0\r\nfictional-answer', duration_seconds: 60 }); await start
  s.started(); assert.equal(s.states.length, count); assert.equal(s.order.includes('remote'), false); assert.deepEqual(s.hangups, ['fictional-session']); assert.equal(s.creationSignal(), undefined); s.released()
})
test('ICE timeout cleans up, never POSTs, and cannot resume on late ICE', async () => {
  const s = setup({ waitForIce: true }); const start = s.voice.start(); await flush()
  s.clock.tick(10000); await start; assert.equal(s.last().status, 'error')
  s.peer.iceGatheringState = 'complete'; event(s.peer, 'icegatheringstatechange')
  assert.equal(s.counts().postCalls, 0); s.released(); s.dispose()
})
test('permission and session.started watchdogs are finite and release late resources', async () => {
  const permission = deferred(), s = setup({ media: () => permission.promise })
  const start = s.voice.start(); await flush(); s.clock.tick(60000)
  assert.equal(s.last().status, 'error'); permission.resolve(s.mic); await start; assert.equal(s.mic.track.stopped, true); s.dispose()
  const connected = setup(); await connected.voice.start(); connected.clock.tick(45000)
  assert.equal(connected.last().status, 'error'); connected.released(); connected.dispose()
})
test('configured duration closes even a muted session and clears timers', async () => {
  const s = setup(); await s.voice.start(); s.started(); s.voice.toggleMute()
  s.clock.tick(60000); assert.equal(s.last().status, 'closing'); s.clock.tick(CLOSE_WAIT_MS)
  assert.equal(s.last().status, 'closed'); assert.match(s.last().message, /Microphone off/); s.released(); s.dispose()
})
test('provider, malformed-event, mismatched-session, peer and data-channel failures are sanitized', async () => {
  const failures = [s => s.channel.message({ type: 'error', message: 'PRIVATE_PROVIDER_DETAIL' }),
    s => event(s.channel, 'message', { data: '{PRIVATE_PROVIDER_DETAIL' }),
    s => s.channel.message({ type: 'session.started', session: { id: 'wrong' } }),
    s => { s.peer.connectionState = 'failed'; event(s.peer, 'connectionstatechange') },
    s => event(s.channel, 'error'), s => event(s.channel, 'close'), s => event(s.mic.track, 'ended')]
  for (const fail of failures) {
    const s = setup(); await s.voice.start(); fail(s)
    assert.equal(s.last().status, 'error'); assert.doesNotMatch(JSON.stringify(s.states), /PRIVATE_PROVIDER_DETAIL/)
    assert.match(s.last().message, /text choices/); s.released(); s.dispose()
  }
})
test('timed transcripts preserve exact deltas, interval ordering and overlap without invented turns', async () => {
  const s = setup(); await s.voice.start(); s.started()
  s.channel.message({ type: 'session.input_transcript.delta', delta: ' again', start_ms: 1100, end_ms: 1200 })
  s.channel.message({ type: 'session.input_transcript.delta', delta: 'Hello ', start_ms: 1000, end_ms: 1100 })
  s.channel.message({ type: 'session.output_transcript.delta', delta: 'Hi', start_ms: 1050, end_ms: 1150 })
  assert.deepEqual(s.last().transcripts.map(g => [g.speaker, g.text]), [['You', 'Hello '], ['Pause', 'Hi'], ['You', ' again']])
  s.channel.message({ type: 'session.input_transcript.delta', delta: ' again', start_ms: 1200, end_ms: 1300 })
  assert.equal(s.last().transcripts.at(-1).text, ' again again')
  const before = s.last().transcripts
  s.channel.message({ type: 'session.input_transcript.delta', delta: 'invalid', start_ms: -1, end_ms: 2 })
  assert.deepEqual(s.last().transcripts, before)
  s.voice.stop()
  assert.equal(s.audio.pauses, 0); assert.equal(s.peer.closed, false)
  s.channel.message({ type: 'session.output_transcript.delta', delta: ' goodbye', start_ms: 1400, end_ms: 1500 })
  assert.equal(s.last().transcripts.at(-1).text, ' goodbye')
  s.channel.message({ type: 'session.closed' })
  assert.equal(s.last().closure, 'confirmed'); s.released(); s.dispose()
})
test('disconnect while closing reports incomplete finalization', async () => {
  const s = setup(); await s.voice.start(); s.started(); s.voice.stop()
  event(s.channel, 'close')
  assert.equal(s.last().closure, 'unconfirmed')
  assert.match(s.last().message, /incomplete/); s.released(); s.dispose()
})
test('session HTTP failure has no retries and releases the microphone', async () => {
  const s = setup({ post: async () => { throw Error('PRIVATE_PROVIDER_DETAIL') } }); await s.voice.start()
  assert.equal(s.last().status, 'error'); assert.equal(s.counts().postCalls, 1)
  assert.doesNotMatch(s.last().message, /PRIVATE/); s.released(); s.dispose()
})
test('voice API sends only SDP to FastAPI and projects validated response fields', async () => {
  const calls = [], abort = new AbortController()
  const api = createVoiceAPI(async (path, options) => {
    calls.push({ path, options })
    return { ok: true, json: async () => path.endsWith('config')
      ? { status: 'configured', duration_seconds: 60, private: 'ignored' }
      : { session_id: 'fictional-id', sdp: 'v=0\r\nanswer', duration_seconds: 60, private: 'ignored' } }
  })
  assert.deepEqual(await api.config(abort.signal), { status: 'configured', duration_seconds: 60 })
  assert.deepEqual(await api.createSession('v=0\r\noffer', abort.signal), { session_id: 'fictional-id', sdp: 'v=0\r\nanswer', duration_seconds: 60 })
  assert.equal(calls[1].path, '/api/voice/sessions'); assert.equal(calls[1].options.method, 'POST')
  assert.deepEqual(JSON.parse(calls[1].options.body), { sdp: 'v=0\r\noffer' })
  assert.deepEqual(calls[1].options.headers, { 'Content-Type': 'application/json' }); assert.equal('keepalive' in calls[1].options, false)
  abort.abort(); assert.equal(calls[1].options.signal.aborted, true)
})
test('voice API rejects unavailable/malformed responses without echoing provider details', async () => {
  const signal = new AbortController().signal
  for (const body of [null, {}, { status: 'other', duration_seconds: 60 }, { status: 'configured', duration_seconds: 0 }]) {
    const api = createVoiceAPI(async () => ({ ok: true, json: async () => body }))
    await assert.rejects(api.config(signal), /Invalid voice response/)
  }
  for (const body of [{}, { session_id: 'bad\nid', sdp: 'v=0', duration_seconds: 60 }, { session_id: 'id', sdp: 'v=0' + 'x'.repeat(65536), duration_seconds: 60 }]) {
    const api = createVoiceAPI(async () => ({ ok: true, json: async () => body }))
    await assert.rejects(api.createSession('offer', signal), /Invalid voice response/)
  }
  const api = createVoiceAPI(async () => ({ ok: false, text: async () => 'PRIVATE_PROVIDER_DETAIL' }))
  await assert.rejects(api.config(signal), /^Error: Voice unavailable$/)
})

test('session.closed acknowledges End early; no HTTP fallback or duplicate End command', async () => {
  const s = setup(); await s.voice.start(); s.started(); s.attach(); await flush()
  s.voice.stop(); s.voice.stop(); assert.equal(s.mic.track.stopped, true)
  assert.equal(s.peer.closed, false); assert.equal(s.audio.pauses, 0)
  assert.deepEqual(s.channel.sent, [{ type: 'session.close' }])
  s.channel.message({ type: 'session.closed' })
  assert.equal(s.last().closure, 'confirmed'); assert.equal(s.last().status, 'closed')
  s.released(); s.clock.tick(CLOSE_WAIT_MS * 2); assert.deepEqual(s.hangups, [])
  s.dispose()
})
test('duplicate Start during Closing and repeated End do not extend the deadline or duplicate work', async () => {
  const s = setup(); await s.voice.start(); s.started(); s.voice.stop()
  s.clock.tick(500); s.voice.stop(); await s.voice.start()
  assert.equal(s.counts().postCalls, 1); assert.equal(s.channel.sent.length, 1)
  s.clock.tick(CLOSE_WAIT_MS - 500); await flush()
  assert.equal(s.last().status, 'closed'); assert.equal(s.last().closure, 'requested')
  assert.match(s.last().message, /unconfirmed|incomplete/); assert.deepEqual(s.hangups, ['fictional-session'])
  s.voice.stop(); assert.equal(s.hangups.length, 1); s.released(); s.dispose()
})
test('late SDP after End requests hangup exactly once without applying the answer or restoring Active', async () => {
  const post = deferred(), s = setup({ post: () => post.promise })
  const starting = s.voice.start(); await flush(); s.voice.stop(); s.clock.tick(CLOSE_WAIT_MS)
  post.resolve({ session_id: 'late-session', sdp: 'v=0\r\nfictional-answer', duration_seconds: 60 })
  await starting; await flush()
  assert.deepEqual(s.hangups, ['late-session']); assert.equal(s.order.includes('remote'), false)
  assert.equal(s.last().status, 'closed'); assert.equal(s.last().closure, 'requested')
  assert.equal(s.states.some(state => state.status === 'active'), false); s.released(); s.dispose()
})
test('late answer while End is still waiting cannot reactivate and does not cause duplicate fallback', async () => {
  const post = deferred(), s = setup({ post: () => post.promise }); const starting = s.voice.start(); await flush()
  s.voice.stop(); post.resolve({ session_id: 'late-session', sdp: 'v=0\r\nfictional-answer', duration_seconds: 60 })
  await starting; assert.equal(s.last().status, 'closing'); assert.equal(s.order.includes('remote'), false)
  s.clock.tick(CLOSE_WAIT_MS); await flush(); assert.deepEqual(s.hangups, ['late-session'])
  s.released(); s.dispose()
})
test('a late old result cannot change a new active session or its audio', async () => {
  const old = deferred(); let posts = 0
  const s = setup({ fresh: true, post: () => ++posts === 1 ? old.promise : Promise.resolve({ session_id: 'new-session', sdp: 'v=0\r\nfictional-answer', duration_seconds: 60 }) })
  const first = s.voice.start(); await flush(); s.voice.stop(); s.clock.tick(CLOSE_WAIT_MS)
  await s.voice.start(); s.channel.message({ type: 'session.started', session: { id: 'new-session' } }); s.attach(); await flush()
  const count = s.states.length, plays = s.audio.plays
  old.resolve({ session_id: 'old-session', sdp: 'v=0\r\nfictional-answer', duration_seconds: 60 }); await first; await flush()
  assert.deepEqual(s.hangups, ['old-session']); assert.equal(s.states.length, count)
  assert.equal(s.last().status, 'active'); assert.equal(s.peer.closed, false); assert.equal(s.mic.track.stopped, false)
  assert.equal(s.audio.plays, plays); s.dispose(); s.released()
})
test('hangup failure preserves local cleanup and reports unconfirmed closure without provider details', async () => {
  const s = setup({ hangup: async () => { throw Error('PRIVATE_PROVIDER_DETAIL') } })
  await s.voice.start(); s.started(); s.voice.stop(); s.clock.tick(CLOSE_WAIT_MS); await flush()
  assert.equal(s.last().status, 'closed'); assert.equal(s.last().closure, 'unconfirmed')
  assert.doesNotMatch(JSON.stringify(s.states), /PRIVATE_PROVIDER_DETAIL/); s.released(); s.dispose()
})
test('each new conversation uses fresh microphone/peer/channel and no retained conversation state', async () => {
  const s = setup({ fresh: true }); await s.voice.start(); s.started(); s.voice.toggleMute()
  const mic = s.mic, peer = s.peer, channel = s.channel
  s.channel.message({ type: 'session.input_transcript.delta', delta: 'FICTIONAL_PRIVATE_TRANSCRIPT' })
  s.voice.stop(); s.channel.message({ type: 'session.closed' }); await s.voice.start()
  assert.notEqual(s.mic, mic); assert.notEqual(s.peer, peer); assert.notEqual(s.channel, channel)
  assert.equal(s.mic.track.enabled, true); assert.equal(s.last().closure, 'none')
  assert.equal(s.last().audioBlocked, false); assert.equal(s.counts().postCalls, 2)
  assert.doesNotMatch(JSON.stringify(s.states), /FICTIONAL_PRIVATE_TRANSCRIPT/)
  s.dispose(); s.released()
})
for (const path of ['unmount', 'navigation', 'crisis', 'page exit', 'hidden', 'duration']) {
  test(`${path} stops capture immediately and cleans the bounded closing session`, async () => {
    const s = setup(), page = new EventTarget(), host = new EventTarget(); page.visibilityState = 'visible'
    const lifecycle = bindVoiceLifecycle(s.voice, page, host)
    await s.voice.start(); s.started(); s.attach(); await flush(); s.voice.toggleMute()
    assert.match(s.last().message, /billing continue/)
    if (path === 'unmount') lifecycle.dispose()
    else if (path === 'page exit') event(host, 'pagehide')
    else if (path === 'hidden') { page.visibilityState = 'hidden'; event(page, 'visibilitychange') }
    else if (path === 'duration') s.clock.tick(60000)
    else lifecycle.leave() // App's Home/choose and independent Crisis Support use this entry.
    assert.equal(s.mic.track.stopped, true); assert.equal(s.peer.closed, false)
    s.clock.tick(CLOSE_WAIT_MS); await flush(); s.released()
    assert.equal(s.channel.sent.length, 1); assert.equal(s.hangups.length, 1)
    lifecycle.dispose(); const calls = s.hangups.length
    event(host, 'pagehide'); page.visibilityState = 'hidden'; event(page, 'visibilitychange'); await flush()
    assert.equal(s.hangups.length, calls)
  })
}
test('hangup HTTP request survives page exit, sends only the ID and never exposes credentials', async () => {
  let request
  const api = createVoiceAPI(async (path, options) => { request = { path, options }; return { ok: true, json: async () => ({ status: 'close_requested' }) } })
  await api.closeSession('fictional-id')
  assert.equal(request.path, '/api/voice/sessions/close'); assert.equal(request.options.keepalive, true)
  assert.deepEqual(JSON.parse(request.options.body), { session_id: 'fictional-id' })
  assert.deepEqual(request.options.headers, { 'Content-Type': 'application/json' })
  for (const result of [{ ok: false }, { ok: true, json: async () => ({ status: 'closed' }) }]) {
    const failed = createVoiceAPI(async () => result)
    await assert.rejects(failed.closeSession('id'), /Voice closure unconfirmed/)
  }
})

test('existing text feedback remains usable after voice configuration, denial or provider failure', async () => {
  const cases = [
    { config: async () => ({ status: 'unconfigured' }) },
    { media: async () => { throw Object.assign(Error('fictional denial'), { name: 'NotAllowedError' }) } },
    { post: async () => { throw Error('fictional provider failure') } },
    { providerEvent: true },
  ]
  for (const options of cases) {
    const s = setup(options)
    await s.voice.start()
    if (options.providerEvent) { s.started(); s.channel.message({ type: 'error', message: 'fictional provider failure' }) }
    assert.equal(s.last().status, 'error')
    const textStates = [], requests = []
    const text = createFeedbackResponder({
      api: { feedbackResponse: async body => {
        requests.push(body)
        return { session_id: 'fictional-session', feedback: body.feedback, status: 'succeeded', saved: true, provider_mode: 'mock',
          messages: [{ role: 'assistant', ordinal: 2, content: 'Feedback noted. You can choose what to do next.' }] }
      } }, sessionId: 'fictional-session', exerciseType: 'grounding_54321',
      localDate: () => '2026-10-26', newId: () => 'fictional-text-request', onState: state => textStates.push(state),
    })
    await text.select('helpful')
    assert.equal(requests.length, 1)
    assert.equal(textStates.at(-1).status, 'ready')
    assert.equal(textStates.at(-1).label, 'Demo response · mock provider')
    assert.equal(s.last().status, 'error')
    text.cancel(); s.dispose()
  }
})


test('diagnostic trace covers minimal offer/answer/start/connection/mute/close without raw data', async () => {
  const s = setup({waitForIce:true}); const start=s.voice.start(); await flush()
  s.peer.iceGatheringState='complete';event(s.peer,'icegatheringstatechange');await start
  s.peer.connectionState='connected';event(s.peer,'connectionstatechange');s.started();s.attach();await flush()
  s.voice.toggleMute();s.voice.toggleMute();s.voice.stop();s.channel.message({type:'session.closed'})
  const stages=s.diagnostics.map(d=>d.stage)
  for(const stage of ['configuration','microphone_requested','microphone_granted','peer_created','channel_created',
    'offer_created','ice_complete','session_request','answer_applied','peer_connected','session_started','active','closing','session_closed']) assert.ok(stages.includes(stage),stage)
  assert.ok(stages.indexOf('channel_created')<stages.indexOf('offer_created'))
  assert.ok(stages.indexOf('ice_complete')<stages.indexOf('session_request'))
  assert.doesNotMatch(JSON.stringify(s.diagnostics),/fictional-session|v=0|SDP/)
  s.released();s.dispose()
})
test('diagnostic failures cannot break the voice lifecycle', async () => {
 const s=setup({diagnosticThrows:true});await s.voice.start();s.started();assert.equal(s.last().status,'active');s.dispose();s.released()
})


test('fresh voice sessions send no instruction/start/update events and keep text source paths separate', async () => {
 const s=setup({fresh:true});await s.voice.start();s.started();s.attach();await flush()
 s.voice.toggleMute();s.voice.toggleMute();s.voice.stop();s.channel.message({type:'session.closed'})
 assert.deepEqual(s.channel.sent,[{type:'session.close'}])
 await s.voice.start();assert.deepEqual(s.channel.sent,[])
 assert.equal(s.counts().postCalls,2)
 s.started();assert.equal(s.last().status,'active');s.dispose();s.released()
})
