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
    <view class="fitness-list-copy plan-card-copy">
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
.plan-card {
  position: relative;
  display: flex;
  min-height: 88px;
  box-sizing: border-box;
  align-items: center;
  gap: var(--mw-space-3);
  margin-bottom: var(--mw-space-3);
  padding: var(--mw-space-4);
  border: 1px solid var(--mw-color-border);
  border-radius: var(--mw-radius-lg);
  background: var(--mw-color-surface);
  box-shadow: var(--mw-shadow-card);
  cursor: grab;
  user-select: none;
  -webkit-touch-callout: none;
  transition:
    background-color 150ms ease,
    box-shadow 180ms ease;
}

.plan-card-accent {
  width: 4px;
  height: 40px;
  flex: 0 0 auto;
  border-radius: var(--mw-radius-pill);
  background: var(--mw-color-primary);
  opacity: 0.72;
  transition:
    height 180ms ease,
    opacity 180ms ease;
}

.plan-card-action {
  display: flex;
  flex: 0 0 auto;
  align-items: center;
  gap: var(--mw-space-4);
}

.plan-card-enter {
  display: flex;
  align-items: center;
  gap: var(--mw-space-1);
  color: var(--mw-color-primary);
}

.plan-card-action-label {
  color: var(--mw-color-text-secondary);
  font-size: var(--mw-font-auxiliary);
}

.plan-card-grip {
  display: grid;
  width: 14px;
  grid-template-columns: repeat(2, 3px);
  gap: 3px;
  opacity: 0.5;
}

.plan-card-grip-dot {
  width: 3px;
  height: 3px;
  border-radius: 50%;
  background: var(--mw-color-text-muted);
}

.plan-card:active,
.plan-card-dragging {
  background: var(--mw-color-primary-soft);
}

.plan-card-dragging {
  cursor: grabbing;
  box-shadow: var(--mw-shadow-raised);
}

.plan-card-dragging .plan-card-accent {
  height: 56px;
  opacity: 1;
}

.plan-card-dragging .plan-card-grip {
  opacity: 1;
}
</style>
