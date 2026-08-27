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
    <button v-if="actionLabel" class="workout-status-action" @click="emit('action', status.state)">
      {{ actionLabel }}
    </button>
  </view>
</template>

<style scoped lang="scss">
.workout-status {
  display: grid;
  min-height: 78rpx;
  box-sizing: border-box;
  grid-template-columns: 14rpx minmax(0, 1fr) auto;
  align-items: center;
  gap: 14rpx;
  margin-bottom: 18rpx;
  padding: 14rpx 16rpx;
  border: 1rpx solid #c7cbc4;
  border-left: 5rpx solid #176b57;
  background: #ebece6;
}

.workout-status-dot {
  width: 12rpx;
  height: 12rpx;
  border-radius: 50%;
  background: #176b57;
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
  font-size: 21rpx;
  font-weight: 700;
}

.workout-status-detail {
  margin-top: 3rpx;
  overflow: hidden;
  color: #6b6f68;
  font-size: 18rpx;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.workout-status-action {
  min-height: 84rpx;
  padding: 0 16rpx;
  border: 1rpx solid #176b57;
  border-radius: 2rpx;
  color: #176b57;
  background: #f4f3ee;
  font-size: 19rpx;
  line-height: 82rpx;
}

.workout-status-unfinished_previous_day {
  border-left-color: #cf533d;
  background: #f1e9e4;
}

.workout-status-unfinished_previous_day .workout-status-dot {
  background: #cf533d;
}

.workout-status-completed_today {
  background: #e7eee9;
}

.workout-status-not_started {
  border-left-color: #8d9089;
  background: transparent;
}

.workout-status-not_started .workout-status-dot {
  background: #8d9089;
}
</style>
