import { test } from 'node:test'
import assert from 'node:assert/strict'
import { createDailyCheckIn, localDateKey, KEY_PREFIX } from '../src/composables/dailyCheckIn.js'
import { getHealth } from '../src/api.js'

function storage() {
  const entries = new Map()
  return { entries, getItem: key => entries.get(key) ?? null, setItem: (key, value) => entries.set(key, value) }
}
test('uses local calendar fields rather than a UTC date or 24h interval', () => {
  const local = { getFullYear: () => 2026, getMonth: () => 9, getDate: () => 19 }
  assert.equal(localDateKey(local), '2026-10-19')
})
test('dismissal survives reload and expires on next calendar day, not 24 hours', () => {
  const store = storage()
  const beforeMidnight = new Date(2026, 9, 19, 23, 59)
  const afterMidnight = new Date(2026, 9, 20, 0, 1)
  const first = createDailyCheckIn(() => store)
  assert.equal(first.isDismissed(beforeMidnight), false)
  first.dismiss(beforeMidnight)
  const reload = createDailyCheckIn(() => store)
  assert.equal(reload.isDismissed(beforeMidnight), true)
  assert.equal(reload.isDismissed(afterMidnight), false)
  assert.deepEqual([...store.entries], [[KEY_PREFIX + '2026-10-19', 'dismissed']])
})
test('blocked storage permits dismissal in this visit without storing mood', () => {
  const state = createDailyCheckIn(() => { throw new Error('Blocked') })
  const date = new Date(2026, 9, 19)
  assert.equal(state.isDismissed(date), false)
  assert.equal(state.storageAvailable, false)
  state.dismiss(date)
  assert.equal(state.isDismissed(date), true)
})
test('date markers synchronize across instances and retain previously dismissed dates', () => {
  const store = storage()
  const a = createDailyCheckIn(() => store)
  const b = createDailyCheckIn(() => store)
  const day1 = new Date(2026, 9, 19)
  const day2 = new Date(2026, 9, 20)
  a.dismiss(day1)
  assert.equal(b.isDismissed(day1), true)
  b.dismiss(day2)
  assert.equal(a.isDismissed(day1), true)
})
test('health client makes the one intended request and rejects failure/malformed status', async () => {
  const health = await getHealth(async (url, options) => {
    assert.equal(url, '/api/health')
    assert.ok(options.signal)
    return { ok: true, json: async () => ({ status: 'ok', database: 'ready' }) }
  })
  assert.equal(health.database, 'ready')
  await assert.rejects(() => getHealth(async () => ({ ok: false })))
  await assert.rejects(() => getHealth(async () => ({ ok: true, json: async () => ({ status: 'error' }) })))
  await assert.rejects(() => getHealth(async () => { throw new Error('Network down') }))
})
