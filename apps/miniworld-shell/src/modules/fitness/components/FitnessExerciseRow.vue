<script setup lang="ts">
import type { FitnessExercise } from '@/modules/fitness'

withDefaults(defineProps<{
  exercise: FitnessExercise
  meta: string
  index?: number
  actionLabel?: string
  actionAriaLabel?: string
  actionTone?: 'primary' | 'danger'
  disabled?: boolean
}>(), {
  index: undefined,
  actionLabel: '',
  actionAriaLabel: '',
  actionTone: 'danger',
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
    <wd-button
      v-if="actionLabel"
      class="fitness-exercise-action"
      :type="actionTone"
      variant="text"
      size="medium"
      :aria-label="actionAriaLabel || `${actionLabel}${exercise.name}`"
      :disabled="disabled"
      @click.stop="emit('action')"
    >
      {{ actionLabel }}
    </wd-button>
    <text v-else class="fitness-arrow" aria-hidden="true">→</text>
  </view>
</template>

<style scoped lang="scss">
.fitness-exercise-row {
  display: flex;
  min-height: 72px;
  align-items: center;
  gap: var(--mw-space-3);
  border-top: 1px solid var(--mw-color-border);
}

.fitness-exercise-row:last-child {
  border-bottom: 1px solid var(--mw-color-border);
}

.fitness-exercise-row-disabled {
  opacity: 0.55;
}

.fitness-exercise-index {
  width: 28px;
  flex: none;
  color: var(--mw-color-accent);
  font-size: var(--mw-font-auxiliary);
  font-weight: 700;
}

.fitness-exercise-action {
  min-width: var(--mw-touch-size);
}
</style>
