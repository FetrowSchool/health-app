export async function getHealth(fetcher = fetch) {
  const response = await fetcher('/api/health', { signal: AbortSignal.timeout(3000) })
  if (!response.ok) throw new Error('Backend unavailable')
  const health = await response.json()
  if (health.status !== 'ok' || health.database !== 'ready') throw new Error('Backend unavailable')
  return health
}

export function createActivityAPI(appId, fetcher = fetch) {
  async function request(path, method = 'GET', body, externalSignal) {
    const response = await fetcher(`/api${path}`, {
      method,
      headers: { 'Content-Type': 'application/json', 'X-App-ID': appId },
      signal: externalSignal ? AbortSignal.any([externalSignal, AbortSignal.timeout(28000)]) : AbortSignal.timeout(3000),
      keepalive: true,
      ...(body === undefined ? {} : { body: JSON.stringify(body) }),
    })
    if (!response.ok) throw new Error('Data not saved')
    return response.json()
  }
  return {
    startSession: payload => request('/sessions', 'POST', payload),
    endSession: (id, payload) => request(`/sessions/${id}`, 'PATCH', payload),
    saveFeedback: (id, feedback) => request(`/sessions/${id}/feedback`, 'PUT', { feedback }),
    feedbackResponse: (body, signal) => request('/feedback-response', 'POST', body, signal),
    saveMood: (day, mood) => request(`/mood-checkins/${day}`, 'PUT', { mood }),
  }
}

// Voice configuration, credentials and prompts belong to FastAPI, not this client.
export function createVoiceAPI(fetcher = fetch) {
  async function request(path, signal, body) {
    const response = await fetcher(`/api/voice/${path}`, {
      method: body === undefined ? 'GET' : 'POST',
      signal: AbortSignal.any([...(signal ? [signal] : []), AbortSignal.timeout(body === undefined ? 3000 : 28000)]),
      cache: 'no-store',
      ...(body === undefined ? {} : { headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) }),
    })
    if (!response.ok) throw new Error('Voice unavailable')
    const result = await response.json()
    if (!Number.isInteger(result?.duration_seconds) || result.duration_seconds < 1 || result.duration_seconds > 300) throw new Error('Invalid voice response')
    return result
  }
  return {
    async closeSession(sessionId) {
      const response = await fetcher('/api/voice/sessions/close', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId }), cache: 'no-store', keepalive: true,
        signal: AbortSignal.timeout(4000),
      })
      if (!response.ok || (await response.json())?.status !== 'close_requested') throw new Error('Voice closure unconfirmed')
    },
    async config(signal) {
      const result = await request('config', signal)
      if (!['configured', 'unconfigured'].includes(result.status)) throw new Error('Invalid voice response')
      return { status: result.status, duration_seconds: result.duration_seconds }
    },
    async createSession(sdp, signal) {
      const result = await request('sessions', signal, { sdp })
      if (typeof result.session_id !== 'string' || !/^[\x21-\x7e]{1,256}$/.test(result.session_id)
        || typeof result.sdp !== 'string' || !result.sdp.startsWith('v=0') || new TextEncoder().encode(result.sdp).length > 65536) throw new Error('Invalid voice response')
      return { session_id: result.session_id, sdp: result.sdp, duration_seconds: result.duration_seconds }
    },
  }
}
