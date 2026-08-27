import type {
  CalendarStats,
  ExerciseLog,
  ExerciseProgress,
  FitnessExercise,
  FitnessPlan,
  HistoryItem,
  SessionDetail,
  WorkoutSet,
} from './types'
import { httpRaw } from '@/http/http'

const base = '/api/v1/fitness'

function request<T>(url: string, method: UniApp.RequestOptions['method'] = 'GET', data?: Record<string, unknown>, query?: Record<string, unknown>) {
  return httpRaw<T>({ url: `${base}${url}`, method, data, query })
}

export const fitnessApi = {
  listPlans: () => request<FitnessPlan[]>('/plans'),
  createPlan: (data: { name: string }) => request<FitnessPlan>('/plans', 'POST', data),
  updatePlan: (id: string, data: { name?: string, sortOrder?: number }) => request<FitnessPlan>(`/plans/${id}`, 'PUT', data),
  archivePlan: (id: string) => request<void>(`/plans/${id}`, 'DELETE'),
  reorderPlans: (ids: string[]) => request<FitnessPlan[]>('/plans/order', 'PUT', { ids }),
  listExercises: (planId: string) => request<FitnessExercise[]>(`/plans/${planId}/exercises`),
  createExercise: (data: { planId: string, name: string, defaultWeight: number, defaultReps: number, weightStep?: number }) => request<FitnessExercise>('/exercises', 'POST', data),
  updateExercise: (id: string, data: { name?: string, defaultWeight?: number, defaultReps?: number, weightStep?: number, sortOrder?: number }) => request<FitnessExercise>(`/exercises/${id}`, 'PUT', data),
  archiveExercise: (id: string) => request<void>(`/exercises/${id}`, 'DELETE'),
  reorderExercises: (planId: string, ids: string[]) => request<FitnessExercise[]>(`/plans/${planId}/exercises/order`, 'PUT', { ids }),
  getActiveSession: () => request<SessionDetail | null>('/sessions/active'),
  startSession: (planId: string) => request<SessionDetail>('/sessions', 'POST', { planId }),
  getSession: (id: string) => request<SessionDetail>(`/sessions/${id}`),
  finishSession: (id: string) => request<SessionDetail>(`/sessions/${id}/finish`, 'POST'),
  getExerciseLog: (sessionId: string, exerciseId: string) => request<ExerciseLog>(`/sessions/${sessionId}/exercises/${exerciseId}`),
  addSet: (sessionId: string, data: { exerciseId: string, weight: number, reps: number, clientRequestId: string }) => request<WorkoutSet>(`/sessions/${sessionId}/sets`, 'POST', data),
  updateSet: (id: string, data: { weight?: number, reps?: number }) => request<WorkoutSet>(`/sets/${id}`, 'PUT', data),
  deleteSet: (id: string) => request<void>(`/sets/${id}`, 'DELETE'),
  history: (limit = 100) => request<HistoryItem[]>('/history', 'GET', undefined, { limit }),
  calendar: (start: string, end: string) => request<CalendarStats>('/stats/calendar', 'GET', undefined, { start, end }),
  progress: (exerciseId: string) => request<ExerciseProgress>(`/stats/exercises/${exerciseId}/progress`),
}

export type FitnessApi = typeof fitnessApi
