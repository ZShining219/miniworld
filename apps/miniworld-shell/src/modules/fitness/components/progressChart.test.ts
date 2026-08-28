import type { ExerciseProgress } from '../types'
import { describe, expect, it } from 'vitest'
import { buildProgressOption } from './progressChart'

const dayProgress: ExerciseProgress = {
  exerciseId: 'exercise-1',
  exerciseName: '杠铃卧推',
  mode: 'day',
  points: [{
    workoutDate: '2026-08-01',
    averageWeight: 78.33,
    minWeight: 75,
    maxWeight: 80,
    setCount: 3,
    sessionCount: 1,
  }],
}

const setProgress: ExerciseProgress = {
  exerciseId: 'exercise-1',
  exerciseName: '杠铃卧推',
  mode: 'set',
  points: [{
    workoutDate: '2026-08-01',
    sessionId: 'session-1',
    completedAt: '2026-08-01T10:00:00Z',
    setOrder: 1,
    weight: 80,
    reps: 8,
  }],
}

describe('fitness progress chart option', () => {
  it('uses daily average weight for the day line chart', () => {
    const option = buildProgressOption(dayProgress, 'day', 'line')
    expect(option.xAxis).toMatchObject({ data: ['08-01'] })
    expect(option.series).toMatchObject([{ type: 'line', data: [78.33] }])
  })

  it('uses each completed set for the set bar chart', () => {
    const option = buildProgressOption(setProgress, 'set', 'bar')
    expect(option.xAxis).toMatchObject({ data: ['08-01 #1'] })
    expect(option.series).toMatchObject([{ type: 'bar', data: [80] }])
  })

  it('keeps chart data empty while a different mode is loading', () => {
    const option = buildProgressOption(dayProgress, 'set', 'line')
    expect(option.xAxis).toMatchObject({ data: [] })
    expect(option.series).toMatchObject([{ data: [] }])
  })
})
