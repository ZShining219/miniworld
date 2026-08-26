import type { FitnessDraft } from './types'

const key = (exerciseId: string) => `miniworld-fitness-draft-v2:${exerciseId}`

export function loadFitnessDraft(exerciseId: string): FitnessDraft | null {
  const value = uni.getStorageSync(key(exerciseId)) as FitnessDraft | null
  return value && Number.isFinite(value.weight) && Number.isFinite(value.reps) ? value : null
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
