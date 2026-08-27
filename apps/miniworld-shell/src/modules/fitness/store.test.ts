import type { ExerciseLog, FitnessPlan, SessionDetail } from './types'
import { describe, expect, it, vi } from 'vitest'
import { createFitnessStore } from './store'

vi.mock('./api', () => ({ fitnessApi: {} }))

const plan: FitnessPlan = {
  id: 'plan-1',
  name: '胸',
  sortOrder: 0,
  exerciseCount: 2,
  createdAt: '',
  updatedAt: '',
}

const plans: FitnessPlan[] = [
  plan,
  { ...plan, id: 'plan-2', name: '背', sortOrder: 1 },
  { ...plan, id: 'plan-3', name: '肩', sortOrder: 2 },
  { ...plan, id: 'plan-4', name: '臀腿', sortOrder: 3 },
]

const session: SessionDetail = {
  id: 'session-1',
  planId: plan.id,
  planNameSnapshot: '胸',
  workoutDate: '2026-08-25',
  status: 'ACTIVE',
  startedAt: '',
  finishedAt: null,
  resumed: false,
  exercises: [],
  totalSetCount: 0,
}

function mockApi() {
  return {
    listPlans: vi.fn().mockResolvedValue(plans),
    createPlan: vi.fn(),
    updatePlan: vi.fn(),
    archivePlan: vi.fn(),
    reorderPlans: vi.fn().mockResolvedValue(plans),
    listExercises: vi.fn(),
    createExercise: vi.fn(),
    updateExercise: vi.fn(),
    archiveExercise: vi.fn(),
    reorderExercises: vi.fn(),
    getActiveSession: vi.fn().mockResolvedValue(session),
    startSession: vi.fn().mockResolvedValue(session),
    getSession: vi.fn().mockResolvedValue(session),
    finishSession: vi.fn().mockResolvedValue({ ...session, status: 'COMPLETED' }),
    getExerciseLog: vi.fn(),
    addSet: vi.fn(),
    updateSet: vi.fn(),
    deleteSet: vi.fn(),
    history: vi.fn().mockResolvedValue([]),
    calendar: vi.fn(),
    progress: vi.fn(),
  }
}

describe('fitness store', () => {
  it('restores an active session while loading home', async () => {
    const api = mockApi()
    const store = createFitnessStore(api)
    await store.refreshHome()
    expect(store.state.plans).toEqual(plans)
    expect(store.state.activeSession?.id).toBe(session.id)
  })

  it('only appends a set after the API persisted it', async () => {
    const api = mockApi()
    const log = { session, exercise: { id: 'exercise-1' }, currentSets: [] } as unknown as ExerciseLog
    api.addSet.mockRejectedValueOnce(new Error('offline'))
    const store = createFitnessStore(api)
    await expect(store.recordSet(log, 80, 8, 'request-1')).rejects.toThrow('offline')
    expect(log.currentSets).toHaveLength(0)

    api.addSet.mockResolvedValueOnce({ id: 'set-1', weight: 80, reps: 8 })
    await store.recordSet(log, 80, 8, 'request-2')
    expect(log.currentSets).toHaveLength(1)
  })

  it('clears active state after finishing the session', async () => {
    const api = mockApi()
    const store = createFitnessStore(api)
    await store.startSession(plan.id)
    expect(store.state.activeSession?.id).toBe(session.id)
    await store.finishSession(session.id)
    expect(store.state.activeSession).toBeNull()
  })

  it('optimistically reorders plans and accepts the persisted response', async () => {
    const api = mockApi()
    const persisted = [plans[2], plans[0], plans[1], plans[3]]
    api.reorderPlans.mockResolvedValueOnce(persisted)
    const store = createFitnessStore(api)
    await store.refreshHome()

    const request = store.reorderPlans(persisted.map(item => item.id))
    expect(store.state.plans.map(item => item.id)).toEqual(persisted.map(item => item.id))
    await expect(request).resolves.toBe(true)
    expect(store.state.plans).toEqual(persisted)
  })

  it('rolls back failed plan ordering', async () => {
    const api = mockApi()
    api.reorderPlans.mockRejectedValueOnce(new Error('offline'))
    const store = createFitnessStore(api)
    await store.refreshHome()

    await expect(store.reorderPlans(['plan-2', 'plan-1', 'plan-3', 'plan-4'])).rejects.toThrow('offline')
    expect(store.state.plans).toEqual(plans)
    expect(store.state.reorderingPlans).toBe(false)
  })

  it('skips identical or concurrent plan ordering', async () => {
    const api = mockApi()
    let resolveRequest: ((value: FitnessPlan[]) => void) | undefined
    api.reorderPlans.mockImplementationOnce(() => new Promise((resolve) => {
      resolveRequest = resolve
    }))
    const store = createFitnessStore(api)
    await store.refreshHome()

    await expect(store.reorderPlans(plans.map(item => item.id))).resolves.toBe(false)
    const first = store.reorderPlans(['plan-2', 'plan-1', 'plan-3', 'plan-4'])
    await expect(store.reorderPlans(['plan-3', 'plan-2', 'plan-1', 'plan-4'])).resolves.toBe(false)
    expect(api.reorderPlans).toHaveBeenCalledTimes(1)
    resolveRequest?.([plans[1], plans[0], plans[2], plans[3]])
    await expect(first).resolves.toBe(true)
  })
})
