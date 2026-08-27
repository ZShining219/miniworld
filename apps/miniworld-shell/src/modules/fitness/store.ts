import type { FitnessApi } from './api'
import type { ExerciseLog, FitnessPlan, HistoryItem, SessionDetail } from './types'
import { reactive } from 'vue'
import { fitnessApi } from './api'
import { hasSameOrder } from './components/planOrder'

export function createFitnessStore(api: FitnessApi = fitnessApi) {
  const state = reactive<{
    plans: FitnessPlan[]
    activeSession: SessionDetail | null
    recentWorkout: HistoryItem | null
    loading: boolean
    reorderingPlans: boolean
  }>({
    plans: [],
    activeSession: null,
    recentWorkout: null,
    loading: false,
    reorderingPlans: false,
  })

  async function refreshHome() {
    state.loading = true
    try {
      const [plans, active, history] = await Promise.all([
        api.listPlans(),
        api.getActiveSession(),
        api.history(1),
      ])
      state.plans = plans
      state.activeSession = active
      state.recentWorkout = history[0] || null
    }
    finally {
      state.loading = false
    }
  }

  async function startSession(planId: string) {
    const session = await api.startSession(planId)
    state.activeSession = session
    return session
  }

  async function reorderPlans(ids: string[]) {
    const currentIds = state.plans.map(plan => plan.id)
    if (state.reorderingPlans || hasSameOrder(currentIds, ids))
      return false

    const byId = new Map(state.plans.map(plan => [plan.id, plan]))
    const reordered = ids.map(id => byId.get(id)).filter((plan): plan is FitnessPlan => Boolean(plan))
    if (reordered.length !== state.plans.length)
      return false

    const previous = [...state.plans]
    state.reorderingPlans = true
    state.plans = reordered
    try {
      state.plans = await api.reorderPlans(ids)
      return true
    }
    catch (error) {
      state.plans = previous
      throw error
    }
    finally {
      state.reorderingPlans = false
    }
  }

  async function loadSession(sessionId: string) {
    const session = await api.getSession(sessionId)
    if (session.status === 'ACTIVE')
      state.activeSession = session
    return session
  }

  async function finishSession(sessionId: string) {
    const session = await api.finishSession(sessionId)
    state.activeSession = null
    return session
  }

  async function recordSet(log: ExerciseLog, weight: number, reps: number, clientRequestId: string) {
    const set = await api.addSet(log.session.id, {
      exerciseId: log.exercise.id,
      weight,
      reps,
      clientRequestId,
    })
    log.currentSets.push(set)
    if (state.activeSession?.id === log.session.id)
      state.activeSession.totalSetCount += 1
    return set
  }

  return { state, refreshHome, reorderPlans, startSession, loadSession, finishSession, recordSet }
}

const fitnessStore = createFitnessStore()

export function useFitnessStore() {
  return fitnessStore
}
