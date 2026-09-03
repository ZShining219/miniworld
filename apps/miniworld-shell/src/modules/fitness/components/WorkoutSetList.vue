<script setup lang="ts">
import type { WorkoutSet } from '@/modules/fitness'

withDefaults(defineProps<{
  sets: WorkoutSet[]
  showRepsUnit?: boolean
  emphasized?: boolean
}>(), { showRepsUnit: false, emphasized: false })
</script>

<template>
  <view class="workout-set-list" :class="{ 'workout-set-list-emphasized': emphasized }">
    <view v-for="set in sets" :key="set.id" class="workout-set-row">
      <text class="workout-set-order">{{ String(set.setOrder).padStart(2, '0') }}</text>
      <text class="workout-set-value">{{ set.weight }} kg × {{ set.reps }}{{ showRepsUnit ? ' 次' : '' }}</text>
    </view>
  </view>
</template>

<style scoped lang="scss">
.workout-set-list {
  overflow: hidden;
  border: 1px solid var(--mw-color-border);
  border-radius: var(--mw-radius-md);
}

.workout-set-row {
  display: grid;
  grid-template-columns: 40px minmax(0, 1fr);
  min-height: var(--mw-touch-size);
  align-items: center;
  padding: 0 var(--mw-space-3);
  border-bottom: 1px solid var(--mw-color-border);
  font-size: var(--mw-font-body);
}

.workout-set-list-emphasized .workout-set-row {
  min-height: 52px;
}

.workout-set-row:last-child {
  border-bottom: 0;
}

.workout-set-order {
  color: var(--mw-color-text-muted);
  font-variant-numeric: tabular-nums;
}

.workout-set-value {
  font-weight: 650;
}
</style>
