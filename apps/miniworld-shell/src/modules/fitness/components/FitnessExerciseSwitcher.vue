<script setup lang="ts">
import type { SessionExerciseSummary } from '@/modules/fitness'

const props = withDefaults(defineProps<{
  exercises: SessionExerciseSummary[]
  currentId: string
  disabled?: boolean
}>(), { disabled: false })

const emit = defineEmits<{ select: [exerciseId: string] }>()

function select(exerciseId: string) {
  if (!props.disabled && exerciseId !== props.currentId)
    emit('select', exerciseId)
}
</script>

<template>
  <view class="exercise-switcher">
    <view class="exercise-switcher-heading">
      <text class="exercise-switcher-label">本次动作</text>
      <text class="exercise-switcher-hint">左右滑动切换</text>
    </view>
    <scroll-view
      class="exercise-switcher-scroll"
      scroll-x
      :scroll-into-view="`exercise-switch-${currentId}`"
      :show-scrollbar="false"
    >
      <view class="exercise-switcher-track">
        <button
          v-for="item in exercises"
          :id="`exercise-switch-${item.exercise.id}`"
          :key="item.exercise.id"
          class="exercise-switcher-item"
          :class="{ 'exercise-switcher-item-active': item.exercise.id === currentId }"
          :disabled="disabled"
          :aria-current="item.exercise.id === currentId ? 'page' : undefined"
          @click="select(item.exercise.id)"
        >
          <text class="exercise-switcher-name">{{ item.exercise.name }}</text>
          <text class="exercise-switcher-count">今日 {{ item.completedSetCount }} 组</text>
        </button>
      </view>
    </scroll-view>
  </view>
</template>

<style scoped lang="scss">
.exercise-switcher {
  padding: 24rpx 0 22rpx;
  border-bottom: 1rpx solid #c9c8c1;
}

.exercise-switcher-heading {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-bottom: 14rpx;
}

.exercise-switcher-label {
  font-size: 22rpx;
  font-weight: 700;
}

.exercise-switcher-hint {
  color: #777a73;
  font-size: 17rpx;
}

.exercise-switcher-scroll {
  width: 100%;
  white-space: nowrap;
}

.exercise-switcher-track {
  display: inline-flex;
  gap: 10rpx;
  padding-right: 24rpx;
}

.exercise-switcher-item {
  display: inline-flex;
  min-width: 176rpx;
  min-height: 78rpx;
  flex-direction: column;
  align-items: flex-start;
  justify-content: center;
  padding: 10rpx 16rpx;
  border: 1rpx solid #aaa9a2;
  border-radius: 2rpx;
  color: #343a35;
  background: transparent;
  line-height: 1.25;
  text-align: left;
}

.exercise-switcher-item-active {
  border-color: #176b57;
  color: #fff;
  background: #176b57;
}

.exercise-switcher-name,
.exercise-switcher-count {
  display: block;
  max-width: 240rpx;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.exercise-switcher-name {
  font-size: 21rpx;
  font-weight: 700;
}

.exercise-switcher-count {
  margin-top: 5rpx;
  color: #777a73;
  font-size: 17rpx;
}

.exercise-switcher-item-active .exercise-switcher-count {
  color: #dbe8e2;
}
</style>
