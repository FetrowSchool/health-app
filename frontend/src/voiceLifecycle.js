// A shared cleanup entry for component removal, explicit app navigation and page exit.
export function bindVoiceLifecycle(voice, page = document, host = window) {
  const leave = () => voice.leave()
  const hidden = () => { if (page.visibilityState === 'hidden') leave() }
  page.addEventListener('visibilitychange', hidden)
  host.addEventListener('pagehide', leave)
  let disposed = false
  return {
    leave,
    dispose() {
      if (disposed) return
      disposed = true
      page.removeEventListener('visibilitychange', hidden)
      host.removeEventListener('pagehide', leave)
      voice.dispose()
    },
  }
}
