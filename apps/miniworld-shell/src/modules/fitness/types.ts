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

export interface ProgressPoint {
  workoutDate: string
  sessionId: string
  maxWeight: number
}

export interface ExerciseProgress {
  exerciseId: string
  exerciseName: string
  points: ProgressPoint[]
}

export interface FitnessDraft {
  weight: number
  reps: number
}
