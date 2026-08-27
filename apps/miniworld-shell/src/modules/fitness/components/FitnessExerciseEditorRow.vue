<script setup lang="ts">
import type { FitnessExercise } from '@/modules/fitness'
import ExerciseDefaultsFields from './ExerciseDefaultsFields.vue'

defineProps<{
  exercise: FitnessExercise
  first: boolean
  last: boolean
}>()

const emit = defineEmits<{
  'save': []
  'archive': []
  'move': [direction: number]
  'update:name': [value: string]
  'update:weight': [value: number]
  'update:reps': [value: number]
}>()
</script>

<template>
  <view class="exercise-editor-row">
    <ExerciseDefaultsFields
      :name="exercise.name"
      :weight="exercise.defaultWeight"
      :reps="exercise.defaultReps"
      @update:name="emit('update:name', $event)"
      @update:weight="emit('update:weight', $event)"
      @update:reps="emit('update:reps', $event)"
    />
    <view class="exercise-editor-actions">
      <button class="fitness-icon-button" aria-label="上移" :disabled="first" @click="emit('move', -1)">
        ↑
      </button>
      <button class="fitness-icon-button" aria-label="下移" :disabled="last" @click="emit('move', 1)">
        ↓
      </button>
      <button class="fitness-secondary" @click="emit('save')">
        保存
      </button>
      <button class="fitness-danger" @click="emit('archive')">
        归档
      </button>
    </view>
  </view>
</template>

<style scoped lang="scss">
.exercise-editor-row {
  padding: 24rpx 0;
  border-top: 1rpx solid #d5d3cc;
}

.exercise-editor-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
  margin-top: 16rpx;
}
</style>
