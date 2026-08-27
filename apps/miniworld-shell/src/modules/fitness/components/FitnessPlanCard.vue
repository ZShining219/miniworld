<script setup lang="ts">
import type { FitnessPlan } from '@/modules/fitness'

defineProps<{
  plan: FitnessPlan
  dragging?: boolean
}>()

const emit = defineEmits<{ select: [] }>()
</script>

<template>
  <view
    class="plan-card"
    :class="{ 'plan-card-dragging': dragging }"
    role="button"
    :aria-label="`进入${plan.name}训练，长按可调整顺序`"
    @click="emit('select')"
  >
    <view class="plan-card-accent" aria-hidden="true" />
    <view class="fitness-list-copy">
      <text class="fitness-list-title">{{ plan.name }}</text>
      <text class="fitness-meta">{{ plan.exerciseCount }} 个动作 · 点击查看并选择</text>
    </view>
    <view class="plan-card-action">
      <view class="plan-card-grip" aria-hidden="true">
        <text v-for="dot in 6" :key="dot" class="plan-card-grip-dot" />
      </view>
      <view class="plan-card-enter">
        <text class="plan-card-action-label">进入</text>
        <text class="fitness-arrow">↗</text>
      </view>
    </view>
  </view>
</template>

<style scoped lang="scss">
@import '@/modules/fitness/fitness.scss';

.plan-card {
  position: relative;
  display: flex;
  min-height: 132rpx;
  box-sizing: border-box;
  align-items: center;
  gap: 20rpx;
  padding: 0 18rpx 0 24rpx;
  border-top: 1rpx solid #d5d3cc;
  background: #f4f3ee;
  cursor: grab;
  user-select: none;
  -webkit-touch-callout: none;
  transition:
    background-color 150ms ease,
    box-shadow 180ms ease;
}

.plan-card::after {
  position: absolute;
  right: 18rpx;
  bottom: 0;
  left: 24rpx;
  height: 1rpx;
  background: transparent;
  content: '';
}

.plan-card-accent {
  width: 5rpx;
  height: 50rpx;
  flex: 0 0 auto;
  border-radius: 999rpx;
  background: #176b57;
  opacity: 0.26;
  transition:
    height 180ms ease,
    opacity 180ms ease;
}

.plan-card-action {
  display: flex;
  flex: 0 0 auto;
  align-items: center;
  gap: 20rpx;
}

.plan-card-enter {
  display: flex;
  align-items: center;
  gap: 8rpx;
  color: #cf533d;
}

.plan-card-action-label {
  color: #777a73;
  font-size: 18rpx;
}

.plan-card-grip {
  display: grid;
  width: 22rpx;
  grid-template-columns: repeat(2, 5rpx);
  gap: 5rpx;
  opacity: 0.42;
}

.plan-card-grip-dot {
  width: 5rpx;
  height: 5rpx;
  border-radius: 50%;
  background: #565b55;
}

.plan-card:active,
.plan-card-dragging {
  background: #ebece6;
}

.plan-card-dragging {
  cursor: grabbing;
  box-shadow: 0 18rpx 44rpx rgba(29, 36, 32, 0.16);
}

.plan-card-dragging .plan-card-accent {
  height: 72rpx;
  opacity: 1;
}

.plan-card-dragging .plan-card-grip {
  opacity: 1;
}
</style>
