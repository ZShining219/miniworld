import type { FitnessWorkoutStatus, HistoryItem, SessionDetail } from './types'

export function localDateKey(value = new Date()) {
  const year = value.getFullYear()
  const month = String(value.getMonth() + 1).padStart(2, '0')
  const day = String(value.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

export function deriveWorkoutStatus(
  active: SessionDetail | null,
  recent: HistoryItem | null,
  today = localDateKey(),
): FitnessWorkoutStatus {
  if (active) {
    return {
      state: active.workoutDate === today ? 'ACTIVE_TODAY' : 'UNFINISHED_PREVIOUS_DAY',
      sessionId: active.id,
      planName: active.planNameSnapshot,
      workoutDate: active.workoutDate,
      totalSetCount: active.totalSetCount,
    }
  }
  if (recent?.session.workoutDate === today) {
    return {
      state: 'COMPLETED_TODAY',
      sessionId: recent.session.id,
      planName: recent.session.planNameSnapshot,
      workoutDate: recent.session.workoutDate,
      totalSetCount: recent.setCount,
    }
  }
  return {
    state: 'NOT_STARTED',
    sessionId: null,
    planName: null,
    workoutDate: null,
    totalSetCount: 0,
  }
}
