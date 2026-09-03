<script setup lang="ts">
import type { FitnessWorkoutStatus, WorkoutStatusState } from '@/modules/fitness'
import FitnessWorkoutStatusBar from './FitnessWorkoutStatusBar.vue'

withDefaults(defineProps<{
  eyebrow: string
  title: string
  subtitle?: string
  error?: string
  compactHeading?: boolean
  workoutStatus?: FitnessWorkoutStatus | null
  workoutActionLabel?: string
}>(), {
  subtitle: '',
  error: '',
  compactHeading: false,
  workoutStatus: null,
  workoutActionLabel: '',
})

const emit = defineEmits<{ workoutAction: [state: WorkoutStatusState] }>()
</script>

<template>
  <view class="fitness-page pt-safe">
    <view class="fitness-shell">
      <FitnessWorkoutStatusBar
        v-if="workoutStatus"
        :status="workoutStatus"
        :action-label="workoutActionLabel"
        @action="emit('workoutAction', $event)"
      />
      <view class="fitness-heading" :class="{ 'fitness-heading-compact': compactHeading }">
        <text class="fitness-eyebrow">{{ eyebrow }}</text>
        <slot name="heading">
          <text class="fitness-title">{{ title }}</text>
          <text v-if="subtitle" class="fitness-subtitle">{{ subtitle }}</text>
        </slot>
      </view>
      <view v-if="error" class="fitness-error" role="alert">
        <text aria-hidden="true">!</text>
        <text>{{ error }}</text>
      </view>
      <slot />
    </view>
  </view>
</template>

<style lang="scss">
@import '@/modules/fitness/fitness.scss';
</style>

<style scoped lang="scss">
.fitness-heading-compact {
  padding-bottom: var(--mw-space-5);
}
</style>
