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
      <wd-button class="fitness-icon-button" type="info" variant="soft" size="medium" aria-label="上移" :disabled="first" @click="emit('move', -1)">
        ↑
      </wd-button>
      <wd-button class="fitness-icon-button" type="info" variant="soft" size="medium" aria-label="下移" :disabled="last" @click="emit('move', 1)">
        ↓
      </wd-button>
      <wd-button class="fitness-secondary" type="primary" variant="soft" size="medium" @click="emit('save')">
        保存
      </wd-button>
      <wd-button class="fitness-danger" type="danger" variant="text" size="medium" @click="emit('archive')">
        归档
      </wd-button>
    </view>
  </view>
</template>

<style scoped lang="scss">
.exercise-editor-row {
  padding: var(--mw-space-5) 0;
  border-top: 1px solid var(--mw-color-border);
}

.exercise-editor-actions {
  display: flex;
  flex-wrap: wrap;
  gap: var(--mw-space-2);
  margin-top: var(--mw-space-4);
}
</style>
