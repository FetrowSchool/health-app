// Native browser transport with injectable devices/peer/audio/clock for offline tests.
// Transcripts are session-local display only; no recording or persistence.
export const CLOSE_WAIT_MS = 5000
export function createVoiceSession({ api, audio, onState, onDiagnostic = () => {},
  mediaDevices = globalThis.navigator?.mediaDevices,
  createPeer = () => new RTCPeerConnection(),
  remoteStream = track => new MediaStream([track]),
  clock = globalThis,
}) {
  let current = null, disposed = false, latest = null
  let state = { status: 'closed', message: 'Microphone off. Text choices remain available.', audioBlocked: false, closure: 'none', transcripts: [] }
  const emit = patch => { state = { ...state, ...patch }; if (!disposed) onState({ ...state }) }
  const alive = a => current === a && !a.released
  const usable = a => alive(a) && !a.ending && !disposed
  const quietly = action => { try { action() } catch { /* Finish releasing other resources. */ } }
  const report = (a, stage, category = 'ok') => { if (!alive(a) || disposed) return; a.stage = stage; quietly(() => onDiagnostic({ stage, category })) }
  const stopTracks = stream => quietly(() => stream?.getTracks().forEach(track => quietly(() => track.stop())))
  const timer = (a, fn, ms) => { const id = clock.setTimeout(() => { a.timers.delete(id); if (alive(a)) fn() }, ms); a.timers.add(id); return id }
  function listen(a, target, type, fn) {
    const handler = event => { if (alive(a)) fn(event) }
    target.addEventListener(type, handler)
    a.listeners.push(() => target.removeEventListener(type, handler))
  }
  function release(a) {
    if (a.released) return
    a.released = true
    const ownsAudio = current === a
    if (ownsAudio) current = null
    a.abort.abort()
    a.timers.forEach(id => clock.clearTimeout(id))
    a.listeners.forEach(remove => quietly(remove))
    stopTracks(a.stream)
    stopTracks(a.remote)
    if (ownsAudio) { quietly(() => audio.pause()); quietly(() => { audio.srcObject = null }) }
    quietly(() => a.channel?.close())
    quietly(() => a.peer?.close())
  }
  function hangup(a, id = a.sessionId) {
    if (!id || a.hangup || a.confirmed) return a.hangup
    const update = closure => {
      if (latest === a && !a.confirmed && ['closed', 'error'].includes(state.status)) emit({
        closure, message: state.status === 'error' ? state.message : closure === 'requested'
          ? 'Microphone off. Provider close requested; finalization incomplete and unconfirmed.'
          : 'Microphone off. Provider finalization incomplete (session.closed not received). Text choices remain available.',
      })
    }
    // Independent bounded keepalive request: never reuse an ended setup's abort signal.
    try { a.hangup = Promise.resolve(api.closeSession(id)).then(() => update('requested'), () => update('unconfirmed')) }
    catch { a.hangup = Promise.resolve(); update('unconfirmed') }
    return a.hangup
  }
  function sendClose(a) {
    if (a.closeSent || !a.startedId || a.startedId !== a.sessionId || a.channel?.readyState !== 'open') return
    try { a.channel.send(JSON.stringify({ type: 'session.close' })); a.closeSent = true } catch { /* HTTP fallback after the short wait. */ }
  }
  function finish(a, confirmed = false) {
    if (a.released) return
    a.confirmed = confirmed
    release(a)
    if (latest === a) emit({ status: 'closed', audioBlocked: false, closure: confirmed ? 'confirmed' : a.sessionId || a.creating ? 'unconfirmed' : 'none',
      message: confirmed ? 'Voice ended. Microphone off; provider session.closed received.'
        : a.sessionId || a.creating ? 'Microphone off. Provider finalization incomplete (session.closed not received). Text choices remain available.'
          : 'Microphone off. Text choices remain available.',
    })
    if (!confirmed) hangup(a)
  }
  function fail(a, message = 'Voice connection failed. You can still use the text choices.') {
    if (!alive(a)) return
    if (a.ending) return finish(a)
    report(a, a.stage || 'startup', 'failed')
    release(a)
    emit({ status: 'error', message, audioBlocked: false, closure: a.sessionId ? 'unconfirmed' : 'none' })
    hangup(a)
  }
  function stop() {
    const a = current
    if (!a || a.ending) return
    a.ending = true
    report(a, 'closing')
    stopTracks(a.stream) // Never wait for the provider before stopping capture.
    // Keep remote audio and transport until session.closed or the bounded timeout.
    a.abort.abort() // Cancel config/ICE, but let an in-flight SDP result reveal its ID.
    a.timers.forEach(id => clock.clearTimeout(id)); a.timers.clear()
    emit({ status: 'closing', message: 'Microphone off. Waiting briefly for voice to close…', audioBlocked: false, closure: 'pending' })
    timer(a, () => finish(a), CLOSE_WAIT_MS)
    sendClose(a)
  }
  async function play(a) {
    const version = ++a.playVersion
    try {
      // This call is synchronous up to play(), including when invoked from a click.
      await audio.play()
      if (usable(a) && version === a.playVersion) emit({ audioBlocked: false })
    } catch {
      if (usable(a) && version === a.playVersion) { report(a, 'playback', 'blocked'); emit({ audioBlocked: true }) }
    }
  }
  function activate(a) {
    if (!usable(a) || !a.answerApplied || !a.startedId || a.started) return
    if (a.startedId !== a.sessionId) return fail(a)
    a.started = true
    report(a, 'active')
    clock.clearTimeout(a.deadline); a.timers.delete(a.deadline)
    emit({ status: 'active', message: 'Microphone on. Speak whenever you choose.' })
  }
  function message(a, event) {
    let data
    try {
      if (typeof event.data !== 'string' || event.data.length > 131072) throw new Error()
      data = JSON.parse(event.data)
      if (!data || typeof data.type !== 'string') throw new Error()
    } catch { return fail(a) }
    if (data.type === 'session.started') {
      if (typeof data.session?.id !== 'string' || !data.session.id) return fail(a)
      report(a, 'session_started')
      a.startedId = data.session.id
      if (a.ending) sendClose(a)
      else activate(a)
    } else if (data.type === 'session.closed') { report(a, 'session_closed'); stopTracks(a.stream); finish(a, true) }
    else if (data.type === 'error') fail(a)
    else if (['session.input_transcript.delta', 'session.output_transcript.delta'].includes(data.type)) {
      if (typeof data.delta !== 'string' || !Number.isFinite(data.start_ms) || !Number.isFinite(data.end_ms)
          || data.start_ms < 0 || data.end_ms < data.start_ms) return
      const speaker = data.type === 'session.input_transcript.delta' ? 'You' : 'Pause'
      // Keep exact fragments and timing. Group by overlapping/adjacent speaker intervals,
      // never infer conversational turns or insert whitespace into model text.
      const fragments = [...state.transcripts.flatMap(group => group.fragments),
        { speaker, delta: data.delta, start_ms: data.start_ms, end_ms: data.end_ms, sequence: a.sequence++ }]
      fragments.sort((x, y) => x.start_ms - y.start_ms || x.sequence - y.sequence)
      const groups = []
      for (const fragment of fragments) {
        const previous = groups.at(-1)
        if (previous && previous.speaker === fragment.speaker && fragment.start_ms <= previous.end_ms) {
          previous.fragments.push(fragment); previous.text += fragment.delta
          previous.end_ms = Math.max(previous.end_ms, fragment.end_ms)
        } else groups.push({ speaker: fragment.speaker, start_ms: fragment.start_ms, end_ms: fragment.end_ms,
          text: fragment.delta, fragments: [fragment] })
      }
      emit({ transcripts: groups })
    }
    // Unknown events do not change configuration or application behavior.
  }
  function waitForIce(a) {
    if (a.peer.iceGatheringState === 'complete') return Promise.resolve()
    return new Promise((resolve, reject) => {
      const done = error => {
        clock.clearTimeout(timeout)
        a.peer.removeEventListener('icegatheringstatechange', changed)
        a.abort.signal.removeEventListener('abort', aborted)
        error ? reject(error) : resolve()
      }
      const changed = () => { if (a.peer.iceGatheringState === 'complete') done() }
      const aborted = () => done(new Error('Cancelled'))
      const timeout = clock.setTimeout(() => done(new Error('ICE timeout')), 10000)
      a.peer.addEventListener('icegatheringstatechange', changed)
      a.abort.signal.addEventListener('abort', aborted, { once: true })
      if (a.abort.signal.aborted) aborted()
      else changed()
    })
  }
  async function start() {
    if (disposed || current || state.status === 'closing') return
    const a = { abort: new AbortController(), timers: new Set(), listeners: [], playVersion: 0, sequence: 0 }
    current = latest = a
    emit({ status: 'permission', message: 'Checking voice setup, then requesting microphone access…', audioBlocked: false, closure: 'none', transcripts: [] })
    a.deadline = timer(a, () => fail(a, 'Microphone setup timed out. You can still use the text choices.'), 60000)
    try {
      if (!mediaDevices?.getUserMedia || !audio) throw new Error('Unsupported browser')
      report(a, 'configuration')
      const config = await api.config(a.abort.signal)
      if (!usable(a)) return
      if (config.status !== 'configured') return fail(a, 'Voice is not configured. You can still use the text choices.')
      emit({ message: 'Allow microphone access to start, or cancel and keep using text.' })
      report(a, 'microphone_requested')
      const stream = await mediaDevices.getUserMedia({ audio: true, video: false })
      if (!usable(a)) { stopTracks(stream); return }
      a.stream = stream
      report(a, 'microphone_granted')
      if (!stream.getAudioTracks().length) throw new Error('No microphone')
      emit({ status: 'connecting', message: 'Connecting voice. You can cancel at any time.' })
      clock.clearTimeout(a.deadline); a.timers.delete(a.deadline)
      a.deadline = timer(a, () => fail(a, 'Voice connection timed out. You can still use the text choices.'), 45000)
      report(a, 'peer_creation')
      a.peer = createPeer()
      report(a, 'peer_created')
      for (const track of stream.getAudioTracks()) {
        a.peer.addTrack(track, stream)
        listen(a, track, 'ended', () => fail(a, 'Microphone access ended. You can still use the text choices.'))
      }
      listen(a, a.peer, 'connectionstatechange', () => {
        if (['connected', 'failed', 'disconnected', 'closed'].includes(a.peer.connectionState)) report(a, 'peer_' + a.peer.connectionState)
        if (['failed', 'disconnected', 'closed'].includes(a.peer.connectionState)) fail(a)
      })
      listen(a, a.peer, 'track', event => {
        if (event.track.kind !== 'audio') return
        if (a.ending) { quietly(() => event.track.stop()); return }
        a.remote = event.streams?.[0] || remoteStream(event.track)
        audio.srcObject = a.remote
        play(a)
      })
      a.channel = a.peer.createDataChannel('oai-events')
      listen(a, a.channel, 'message', event => message(a, event))
      listen(a, a.channel, 'open', () => { if (a.ending) sendClose(a) })
      listen(a, a.channel, 'close', () => fail(a))
      listen(a, a.channel, 'error', () => fail(a))
      report(a, 'channel_created')
      report(a, 'offer_creation')
      const offer = await a.peer.createOffer()
      report(a, 'offer_created')
      if (!usable(a)) return
      await a.peer.setLocalDescription(offer)
      if (!usable(a)) return
      report(a, 'ice_gathering')
      await waitForIce(a)
      if (!usable(a)) return
      report(a, 'ice_complete')
      a.creating = true
      // Do not abort this fetch on End: its late session ID is needed for hangup.
      report(a, 'session_request')
      const result = await api.createSession(a.peer.localDescription.sdp)
      a.creating = false
      a.sessionId = result.session_id
      if (!usable(a)) { hangup(a); return }
      timer(a, () => stop('Voice time limit reached. Microphone off.'), result.duration_seconds * 1000)
      report(a, 'answer_application')
      await a.peer.setRemoteDescription({ type: 'answer', sdp: result.sdp })
      if (!usable(a)) { if (!a.confirmed) hangup(a); return }
      report(a, 'answer_applied')
      a.answerApplied = true
      activate(a) // Also handles session.started arriving during setRemoteDescription.
    } catch (error) {
      if (usable(a)) report(a, a.stage || 'startup', ({ NotAllowedError: 'not_allowed', NotFoundError: 'not_found',
        NotReadableError: 'not_readable', SecurityError: 'security', AbortError: 'aborted',
        OperationError: 'operation', InvalidStateError: 'invalid_state' })[error?.name] || 'request_failed')
      if (usable(a)) fail(a, error?.name === 'NotAllowedError'
        ? 'Microphone permission was not granted. You can still use the text choices.' : undefined)
    }
  }
  function toggleMute() {
    const a = current
    if (!a?.started || a.ending || !['active', 'muted'].includes(state.status)) return
    try {
      const muted = state.status !== 'muted'
      a.stream.getAudioTracks().forEach(track => { track.enabled = !muted })
      emit({ status: muted ? 'muted' : 'active', message: muted ? 'Microphone muted. Assistant playback, provider session and billing continue.' : 'Microphone on. Speak whenever you choose.' })
    } catch { fail(a) }
  }
  function dispose() {
    disposed = true
    leave()
  }
  function leave() {
    stop()
    if (current) hangup(current) // Page exit may prevent the grace timer from running.
  }
  emit({})
  return { start, stop, leave, toggleMute, enableAudio: () => { if (current?.remote && usable(current)) return play(current) }, dispose }
}
