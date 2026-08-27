import type { FitnessDraft } from './types'

const key = (exerciseId: string) => `miniworld-fitness-draft-v2:${exerciseId}`

export function loadFitnessDraft(exerciseId: string): FitnessDraft | null {
  const value = uni.getStorageSync(key(exerciseId)) as FitnessDraft | null
  if (!value || !Number.isFinite(value.weight) || !Number.isFinite(value.reps))
    return null
  if (value.clientRequestId !== undefined && typeof value.clientRequestId !== 'string')
    return null
  return value
}

export function saveFitnessDraft(exerciseId: string, draft: FitnessDraft) {
  uni.setStorageSync(key(exerciseId), draft)
}

export function clearFitnessDraft(exerciseId: string) {
  uni.removeStorageSync(key(exerciseId))
}

export function createRequestId() {
  return `fitness-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`
}
