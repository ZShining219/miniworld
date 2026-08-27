import type { HistoryItem, SessionDetail } from './types'
import { describe, expect, it } from 'vitest'
import { deriveWorkoutStatus } from './workoutStatus'

const active = {
  id: 'session-active',
  planId: 'chest',
  planNameSnapshot: '胸',
  workoutDate: '2026-08-27',
  status: 'ACTIVE',
  startedAt: '',
  finishedAt: null,
  resumed: true,
  exercises: [],
  totalSetCount: 4,
} satisfies SessionDetail

const recent = {
  session: { ...active, id: 'session-completed', status: 'COMPLETED' },
  durationSeconds: 1200,
  exerciseCount: 2,
  setCount: 5,
  exercises: [],
} satisfies HistoryItem

describe('fitness workout status', () => {
  it('prioritizes an active workout today', () => {
    expect(deriveWorkoutStatus(active, recent, '2026-08-27')).toMatchObject({
      state: 'ACTIVE_TODAY',
      sessionId: active.id,
      totalSetCount: 4,
    })
  })

  it('distinguishes an unfinished previous-day workout', () => {
    expect(deriveWorkoutStatus({ ...active, workoutDate: '2026-08-26' }, recent, '2026-08-27').state).toBe('UNFINISHED_PREVIOUS_DAY')
  })

  it('reports a completed workout today when none is active', () => {
    expect(deriveWorkoutStatus(null, recent, '2026-08-27')).toMatchObject({
      state: 'COMPLETED_TODAY',
      totalSetCount: 5,
    })
  })

  it('reports not started when there is no workout today', () => {
    expect(deriveWorkoutStatus(null, { ...recent, session: { ...recent.session, workoutDate: '2026-08-26' } }, '2026-08-27').state).toBe('NOT_STARTED')
  })
})
