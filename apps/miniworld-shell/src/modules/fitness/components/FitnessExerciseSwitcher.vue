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
        <wd-button
          v-for="item in exercises"
          :id="`exercise-switch-${item.exercise.id}`"
          :key="item.exercise.id"
          class="exercise-switcher-item"
          type="primary"
          :variant="item.exercise.id === currentId ? 'base' : 'soft'"
          size="medium"
          :disabled="disabled"
          :aria-current="item.exercise.id === currentId ? 'page' : undefined"
          @click="select(item.exercise.id)"
        >
          <text class="exercise-switcher-name">{{ item.exercise.name }}</text>
          <text class="exercise-switcher-count">今日 {{ item.completedSetCount }} 组</text>
        </wd-button>
      </view>
    </scroll-view>
  </view>
</template>

<style scoped lang="scss">
.exercise-switcher {
  margin-bottom: var(--mw-space-4);
  padding: var(--mw-space-4);
  border: 1px solid var(--mw-color-border);
  border-radius: var(--mw-radius-lg);
  background: var(--mw-color-surface);
  box-shadow: var(--mw-shadow-card);
}

.exercise-switcher-heading {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-bottom: var(--mw-space-3);
}

.exercise-switcher-label {
  font-size: var(--mw-font-strong);
  font-weight: 700;
}

.exercise-switcher-hint {
  color: var(--mw-color-text-muted);
  font-size: var(--mw-font-auxiliary);
}

.exercise-switcher-scroll {
  width: 100%;
  white-space: nowrap;
}

.exercise-switcher-track {
  display: inline-flex;
  gap: var(--mw-space-2);
  padding-right: var(--mw-space-4);
}

.exercise-switcher-item {
  display: inline-flex;
  min-width: 132px;
  min-height: 56px;
  flex-direction: column;
  align-items: flex-start;
  justify-content: center;
  padding: var(--mw-space-2) var(--mw-space-3);
  line-height: 1.25;
  text-align: left;
}

.exercise-switcher-name,
.exercise-switcher-count {
  display: block;
  max-width: 180px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.exercise-switcher-name {
  font-size: var(--mw-font-body);
  font-weight: 700;
}

.exercise-switcher-count {
  margin-top: var(--mw-space-1);
  color: var(--mw-color-text-secondary);
  font-size: var(--mw-font-auxiliary);
}

.exercise-switcher-item[aria-current='page'] .exercise-switcher-count {
  color: var(--mw-color-on-primary-muted);
}
</style>
