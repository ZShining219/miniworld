<script setup lang="ts">
import type { FitnessExercise } from '@/modules/fitness'

withDefaults(defineProps<{
  exercise: FitnessExercise
  meta: string
  index?: number
  actionLabel?: string
  actionAriaLabel?: string
  disabled?: boolean
}>(), {
  index: undefined,
  actionLabel: '',
  actionAriaLabel: '',
  disabled: false,
})

const emit = defineEmits<{
  select: []
  action: []
}>()
</script>

<template>
  <view
    class="fitness-exercise-row"
    :class="{ 'fitness-exercise-row-disabled': disabled }"
    role="button"
    :aria-label="`选择${exercise.name}`"
    @click="!disabled && emit('select')"
  >
    <text v-if="index !== undefined" class="fitness-exercise-index">{{ String(index + 1).padStart(2, '0') }}</text>
    <view class="fitness-list-copy">
      <text class="fitness-list-title">{{ exercise.name }}</text>
      <text class="fitness-meta">{{ meta }}</text>
    </view>
    <button
      v-if="actionLabel"
      class="fitness-exercise-action"
      :aria-label="actionAriaLabel || `${actionLabel}${exercise.name}`"
      :disabled="disabled"
      @click.stop="emit('action')"
    >
      {{ actionLabel }}
    </button>
    <text v-else class="fitness-arrow" aria-hidden="true">→</text>
  </view>
</template>

<style scoped lang="scss">
.fitness-exercise-row {
  display: flex;
  min-height: 116rpx;
  align-items: center;
  gap: 18rpx;
  border-top: 1rpx solid #d5d3cc;
}

.fitness-exercise-row:last-child {
  border-bottom: 1rpx solid #d5d3cc;
}

.fitness-exercise-row-disabled {
  opacity: 0.55;
}

.fitness-exercise-index {
  width: 46rpx;
  flex: none;
  color: #cf533d;
  font-family: Georgia, serif;
  font-size: 22rpx;
}

.fitness-exercise-action {
  min-width: 74rpx;
  height: 58rpx;
  padding: 0 12rpx;
  border: 1rpx solid #d5b2a9;
  border-radius: 2rpx;
  color: #a43f2e;
  background: transparent;
  font-size: 19rpx;
  line-height: 54rpx;
}
</style>
