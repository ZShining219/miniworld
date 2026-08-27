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
  border-top: 1rpx solid #d5d3cc;
}

.workout-set-row {
  display: grid;
  grid-template-columns: 50rpx minmax(0, 1fr);
  min-height: 72rpx;
  align-items: center;
  border-bottom: 1rpx solid #d5d3cc;
  font-size: 25rpx;
}

.workout-set-list-emphasized .workout-set-row {
  min-height: 82rpx;
}

.workout-set-order {
  color: #777a73;
  font-family: Georgia, serif;
}

.workout-set-value {
  font-weight: 650;
}
</style>
