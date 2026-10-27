// Store only dismissal markers, never mood values or a distress interpretation.
export const KEY_PREFIX = 'pause.checkin.dismissed.'

export function localDateKey(date = new Date()) {
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}

export function createDailyCheckIn(getStorage = () => window.localStorage) {
  const dismissedThisVisit = new Set()
  let storageAvailable = true
  function isDismissed(date = new Date()) {
    const day = localDateKey(date)
    if (dismissedThisVisit.has(day)) return true
    try {
      return getStorage().getItem(KEY_PREFIX + day) === 'dismissed'
    } catch {
      storageAvailable = false
      return false
    }
  }
  function dismiss(date = new Date()) {
    const day = localDateKey(date)
    dismissedThisVisit.add(day)
    try {
      getStorage().setItem(KEY_PREFIX + day, 'dismissed')
    } catch {
      storageAvailable = false
    }
  }
  return { isDismissed, dismiss, get storageAvailable() { return storageAvailable } }
}
