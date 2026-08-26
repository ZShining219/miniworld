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
    vi.mocked(uni.getStorageSync).mockReturnValue({ weight: 75, reps: 10 })
    expect(loadFitnessDraft('exercise-1')).toEqual({ weight: 75, reps: 10 })
    clearFitnessDraft('exercise-1')
    expect(uni.removeStorageSync).toHaveBeenCalledWith('miniworld-fitness-draft-v2:exercise-1')
  })
})
