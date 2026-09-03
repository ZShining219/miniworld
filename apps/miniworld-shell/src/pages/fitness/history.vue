<script lang="ts" setup>
import type { HistoryItem } from '@/modules/fitness'
import { fitnessApi, useFitnessWorkoutStatus } from '@/modules/fitness'
import FitnessPageShell from '@/modules/fitness/components/FitnessPageShell.vue'

definePage({ style: { navigationBarTitleText: '训练历史' } })

const items = ref<HistoryItem[]>([])
const loading = ref(true)
const error = ref('')
const { workoutStatus, workoutActionLabel, handleWorkoutAction } = useFitnessWorkoutStatus('history')

onShow(async () => {
  loading.value = true
  error.value = ''
  try {
    items.value = await fitnessApi.history()
  }
  catch {
    error.value = '暂时无法读取训练历史。'
  }
  finally {
    loading.value = false
  }
})

function duration(seconds: number) {
  const minutes = Math.max(1, Math.round(seconds / 60))
  return minutes < 60 ? `${minutes} 分钟` : `${Math.floor(minutes / 60)} 小时 ${minutes % 60} 分钟`
}
</script>

<template>
  <FitnessPageShell
    eyebrow="训练记录"
    title="训练历史"
    subtitle="这里只统计已经结束的训练。"
    :error="error"
    :workout-status="workoutStatus"
    :workout-action-label="workoutActionLabel"
    @workout-action="handleWorkoutAction"
  >
    <view v-if="loading" class="fitness-card fitness-loading-state">
      <wd-loading size="22px" />
      <text class="fitness-meta">正在读取训练历史</text>
    </view>
    <view v-else-if="!items.length && !error" class="fitness-card fitness-empty-state">
      <wd-empty tip="还没有已完成的训练" icon-size="72" />
      <text class="fitness-note">结束第一次训练后，动作和组记录会出现在这里。</text>
    </view>

    <view v-for="item in items" :key="item.session.id" class="fitness-card history-session">
      <view class="fitness-row-between history-heading">
        <view>
          <text class="history-date">{{ item.session.workoutDate }}</text>
          <text class="fitness-list-title">{{ item.session.planNameSnapshot }}</text>
        </view>
        <text class="fitness-meta">{{ duration(item.durationSeconds) }}</text>
      </view>
      <view class="history-summary">
        <text>{{ item.exerciseCount }} 个动作</text>
        <text>{{ item.setCount }} 组</text>
      </view>
      <view v-for="exercise in item.exercises" :key="exercise.exerciseId" class="history-exercise">
        <text class="fitness-list-title">{{ exercise.exerciseName }}</text>
        <text v-for="set in exercise.sets" :key="set.id" class="history-set">{{ set.weight }} kg × {{ set.reps }}</text>
      </view>
    </view>
  </FitnessPageShell>
</template>

<style scoped lang="scss">
.history-session {
  padding: var(--mw-space-5) var(--mw-space-4);
}

.history-heading {
  align-items: flex-start;
}

.history-date {
  display: block;
  margin-bottom: var(--mw-space-2);
  color: var(--mw-color-accent);
  font-size: var(--mw-font-body);
  font-weight: 700;
}

.history-summary {
  display: flex;
  gap: var(--mw-space-2);
  margin: var(--mw-space-4) 0 var(--mw-space-5);
  color: var(--mw-color-text-secondary);
  font-size: var(--mw-font-body);
}

.history-summary text {
  padding: var(--mw-space-1) var(--mw-space-2);
  border-radius: var(--mw-radius-pill);
  background: var(--mw-color-surface-muted);
}

.history-exercise {
  padding: var(--mw-space-4) 0;
  border-top: 1px solid var(--mw-color-border);
}

.history-set {
  display: block;
  margin-top: var(--mw-space-2);
  color: var(--mw-color-text-secondary);
  font-size: var(--mw-font-body);
  font-variant-numeric: tabular-nums;
}
</style>
