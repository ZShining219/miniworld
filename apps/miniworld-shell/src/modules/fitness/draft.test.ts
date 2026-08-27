import { beforeEach, describe, expect, it, vi } from 'vitest'
import { clearFitnessDraft, loadFitnessDraft, saveFitnessDraft } from './draft'

describe('fitness draft', () => {
  beforeEach(() => {
    vi.mocked(uni.getStorageSync).mockReturnValue(null)
  })

  it('stores only the unsaved weight and reps draft', () => {
    saveFitnessDraft('exercise-1', { weight: 80, reps: 8 })
    expect(uni.setStorageSync).toHaveBeenCalledWith(
      'miniworld-fitness-draft-v2:exercise-1',
      { weight: 80, reps: 8 },
    )
  })

  it('restores and clears a valid draft', () => {
    vi.mocked(uni.getStorageSync).mockReturnValue({ weight: 75, reps: 10, clientRequestId: 'request-retry-1' })
    expect(loadFitnessDraft('exercise-1')).toEqual({ weight: 75, reps: 10, clientRequestId: 'request-retry-1' })
    clearFitnessDraft('exercise-1')
    expect(uni.removeStorageSync).toHaveBeenCalledWith('miniworld-fitness-draft-v2:exercise-1')
  })

  it('rejects a malformed persisted request id', () => {
    vi.mocked(uni.getStorageSync).mockReturnValue({ weight: 75, reps: 10, clientRequestId: 123 })
    expect(loadFitnessDraft('exercise-1')).toBeNull()
  })
})
