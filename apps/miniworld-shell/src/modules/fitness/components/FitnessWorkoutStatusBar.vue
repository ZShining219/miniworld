<script setup lang="ts">
import type { FitnessWorkoutStatus, WorkoutStatusState } from '@/modules/fitness'
import { computed } from 'vue'

const props = withDefaults(defineProps<{
  status: FitnessWorkoutStatus
  actionLabel?: string
}>(), { actionLabel: '' })

const emit = defineEmits<{ action: [state: WorkoutStatusState] }>()

const copy = computed(() => {
  const status = props.status
  if (status.state === 'ACTIVE_TODAY')
    return { label: '今日训练进行中', detail: `${status.planName} · ${status.totalSetCount} 组` }
  if (status.state === 'UNFINISHED_PREVIOUS_DAY')
    return { label: '存在未结束训练', detail: `${status.workoutDate} · ${status.planName} · ${status.totalSetCount} 组` }
  if (status.state === 'COMPLETED_TODAY')
    return { label: '今日训练已完成', detail: `${status.planName} · ${status.totalSetCount} 组` }
  return { label: '今日尚未训练', detail: '选择一个部位开始' }
})
</script>

<template>
  <view class="workout-status" :class="`workout-status-${status.state.toLowerCase()}`">
    <view class="workout-status-dot" aria-hidden="true" />
    <view class="workout-status-copy">
      <text class="workout-status-label">{{ copy.label }}</text>
      <text class="workout-status-detail">{{ copy.detail }}</text>
    </view>
    <wd-button
      v-if="actionLabel"
      class="workout-status-action"
      type="primary"
      variant="soft"
      size="medium"
      @click="emit('action', status.state)"
    >
      {{ actionLabel }}
    </wd-button>
  </view>
</template>

<style scoped lang="scss">
.workout-status {
  display: grid;
  min-height: 76px;
  box-sizing: border-box;
  grid-template-columns: 10px minmax(0, 1fr) auto;
  align-items: center;
  gap: var(--mw-space-3);
  margin-bottom: var(--mw-space-3);
  padding: var(--mw-space-3) var(--mw-space-4);
  border: 1px solid var(--mw-color-border);
  border-radius: var(--mw-radius-lg);
  background: var(--mw-color-primary-soft);
}

.workout-status-dot {
  width: 9px;
  height: 9px;
  border-radius: 50%;
  background: var(--mw-color-primary);
  box-shadow: 0 0 0 4px var(--mw-color-primary-soft);
}

.workout-status-copy {
  min-width: 0;
}

.workout-status-label,
.workout-status-detail {
  display: block;
  line-height: 1.35;
}

.workout-status-label {
  font-size: var(--mw-font-strong);
  font-weight: 700;
}

.workout-status-detail {
  margin-top: var(--mw-space-1);
  overflow: hidden;
  color: var(--mw-color-text-secondary);
  font-size: var(--mw-font-body);
  text-overflow: ellipsis;
  white-space: nowrap;
}

.workout-status-action {
  min-width: 96px;
}

.workout-status-unfinished_previous_day {
  background: var(--mw-color-danger-soft);
}

.workout-status-unfinished_previous_day .workout-status-dot {
  background: var(--mw-color-danger);
  box-shadow: 0 0 0 4px var(--mw-color-danger-soft);
}

.workout-status-completed_today {
  background: var(--mw-color-primary-soft);
}

.workout-status-not_started {
  background: var(--mw-color-surface);
}

.workout-status-not_started .workout-status-dot {
  background: var(--mw-color-text-muted);
  box-shadow: 0 0 0 4px var(--mw-color-surface-muted);
}

@media (max-width: 359px) {
  .workout-status {
    grid-template-columns: 8px minmax(0, 1fr);
  }

  .workout-status-action {
    grid-column: 2;
    width: 100%;
  }
}
</style>
