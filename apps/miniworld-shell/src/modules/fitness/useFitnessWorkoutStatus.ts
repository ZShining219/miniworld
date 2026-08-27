import type { WorkoutStatusState } from './types'
import { computed } from 'vue'
import { useFitnessStore } from './store'

type FitnessStatusContext = 'index' | 'plan' | 'exercise' | 'history' | 'other'

export function useFitnessWorkoutStatus(context: FitnessStatusContext, autoRefresh = true) {
  const store = useFitnessStore()

  if (autoRefresh) {
    onShow(async () => {
      try {
        await store.refreshWorkoutStatus()
      }
      catch {
        // Page-specific data errors remain owned by each page.
      }
    })
  }

  const workoutStatus = computed(() => store.state.workoutStatus)
  const workoutActionLabel = computed(() => {
    const state = workoutStatus.value?.state
    if (!state)
      return ''
    if ((state === 'ACTIVE_TODAY' || state === 'UNFINISHED_PREVIOUS_DAY')) {
      if (context === 'plan')
        return ''
      return context === 'exercise' ? '训练概览' : (state === 'ACTIVE_TODAY' ? '继续训练' : '继续处理')
    }
    if (state === 'COMPLETED_TODAY')
      return context === 'history' ? '' : '查看记录'
    return context === 'index' ? '' : '选择部位'
  })

  function handleWorkoutAction(state: WorkoutStatusState) {
    const status = workoutStatus.value
    if (!status)
      return
    if ((state === 'ACTIVE_TODAY' || state === 'UNFINISHED_PREVIOUS_DAY') && status.sessionId) {
      const url = `/pages/fitness/plan?sessionId=${status.sessionId}`
      if (context === 'exercise')
        uni.redirectTo({ url })
      else
        uni.navigateTo({ url })
      return
    }
    if (state === 'COMPLETED_TODAY') {
      if (context !== 'history')
        uni.navigateTo({ url: '/pages/fitness/history' })
      return
    }
    if (context !== 'index')
      uni.navigateTo({ url: '/pages/fitness/index' })
  }

  return { workoutStatus, workoutActionLabel, handleWorkoutAction }
}
