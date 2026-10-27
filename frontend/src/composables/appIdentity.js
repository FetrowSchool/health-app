export function applicationIdentity(getStorage = () => window.localStorage, newId = () => crypto.randomUUID()) {
  const key = 'pause.application-id'
  try {
    const existing = getStorage().getItem(key)
    if (/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(existing ?? '')) return existing
    const id = newId()
    getStorage().setItem(key, id)
    return id
  } catch {
    return newId() // This tab/visit only if persistent browser storage is blocked.
  }
}
