import { createVoiceAPI } from './api.js'

// This is the isolated FastAPI app, never an external-provider URL or private key.
export const DIAGNOSTIC_ORIGIN = 'http://127.0.0.1:8001'
export const createDiagnosticAPI = (fetcher = fetch) => createVoiceAPI((path, options) => fetcher(DIAGNOSTIC_ORIGIN + path, options))

export async function probeMicrophone(devices = navigator.mediaDevices) {
  let stream
  try {
    stream = await devices.getUserMedia({ audio: true, video: false })
    return stream.getAudioTracks().length ? 'Microphone granted; all tracks stopped.' : 'No microphone track returned.'
  } catch (error) {
    return ({ NotAllowedError: 'Microphone permission not granted.', NotFoundError: 'No microphone found.',
      NotReadableError: 'Microphone could not be read.' })[error?.name] || 'Microphone check could not complete.'
  } finally {
    stream?.getTracks().forEach(track => { try { track.stop() } catch {} })
  }
}
