export type SessionStatus = 'ACTIVE' | 'COMPLETED'

export interface FitnessPlan {
  id: string
  name: string
  sortOrder: number
  exerciseCount: number
  createdAt: string
  updatedAt: string
}

export interface FitnessExercise {
  id: string
  planId: string
  name: string
  defaultWeight: number
  defaultReps: number
  weightStep: number
  sortOrder: number
  createdAt: string
  updatedAt: string
}

export interface WorkoutSet {
  id: string
  sessionId: string
  exerciseId: string
  exerciseNameSnapshot: string
  weight: number
  reps: number
  setOrder: number
  completedAt: string
}

export interface WorkoutSession {
  id: string
  planId: string
  planNameSnapshot: string
  workoutDate: string
  status: SessionStatus
  startedAt: string
  finishedAt?: string | null
}

export interface SessionExerciseSummary {
  exercise: FitnessExercise
  completedSetCount: number
}

export interface SessionDetail extends WorkoutSession {
  resumed: boolean
  exercises: SessionExerciseSummary[]
  totalSetCount: number
}

export interface ExerciseLog {
  session: WorkoutSession
  exercise: FitnessExercise
  currentSets: WorkoutSet[]
  previousSets: WorkoutSet[]
  suggestedWeight: number
  suggestedReps: number
}

export interface HistoryExercise {
  exerciseId: string
  exerciseName: string
  sets: WorkoutSet[]
}

export interface HistoryItem {
  session: WorkoutSession
  durationSeconds: number
  exerciseCount: number
  setCount: number
  exercises: HistoryExercise[]
}

export interface CalendarStats {
  dates: string[]
}

export type ProgressMode = 'set' | 'day'

/** Legacy response shape kept for callers that omit the mode query. */
export interface ProgressPoint {
  workoutDate: string
  sessionId: string
  maxWeight: number
}

export interface ProgressSetPoint {
  workoutDate: string
  sessionId: string
  completedAt: string
  setOrder: number
  weight: number
  reps: number
}

export interface ProgressDayPoint {
  workoutDate: string
  averageWeight: number
  minWeight: number
  maxWeight: number
  setCount: number
  sessionCount: number
}

export interface ExerciseProgress {
  exerciseId: string
  exerciseName: string
  mode: ProgressMode
  points: ProgressSetPoint[] | ProgressDayPoint[]
}

export interface FitnessDraft {
  weight: number
  reps: number
  clientRequestId?: string
}

export type WorkoutStatusState = 'ACTIVE_TODAY' | 'UNFINISHED_PREVIOUS_DAY' | 'COMPLETED_TODAY' | 'NOT_STARTED'

export interface FitnessWorkoutStatus {
  state: WorkoutStatusState
  sessionId: string | null
  planName: string | null
  workoutDate: string | null
  totalSetCount: number
}
