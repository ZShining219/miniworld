<script setup lang="ts">
interface InputEventLike {
  detail: { value: string }
}

withDefaults(defineProps<{
  name: string
  weight: number
  reps: number
  namePlaceholder?: string
}>(), { namePlaceholder: '例如：上斜哑铃卧推' })

const emit = defineEmits<{
  'update:name': [value: string]
  'update:weight': [value: number]
  'update:reps': [value: number]
}>()

function numberValue(event: InputEventLike): number {
  const value = Number(event.detail.value)
  return Number.isFinite(value) ? value : 0
}
</script>

<template>
  <view class="exercise-default-fields">
    <view class="exercise-default-name">
      <text class="exercise-field-label">动作名称</text>
      <input
        class="fitness-input"
        :value="name"
        :placeholder="namePlaceholder"
        @input="emit('update:name', $event.detail.value)"
      >
    </view>
    <view class="exercise-default-row">
      <view class="exercise-default-field">
        <text class="exercise-field-label">默认重量（kg）</text>
        <input
          class="fitness-input exercise-numeric-input"
          type="digit"
          :value="String(weight)"
          @input="emit('update:weight', numberValue($event))"
        >
      </view>
      <view class="exercise-default-field">
        <text class="exercise-field-label">默认次数（次）</text>
        <input
          class="fitness-input exercise-numeric-input"
          type="number"
          :value="String(reps)"
          @input="emit('update:reps', numberValue($event))"
        >
      </view>
      <slot name="action" />
    </view>
  </view>
</template>

<style scoped lang="scss">
.exercise-default-fields,
.exercise-default-field {
  min-width: 0;
}

.exercise-field-label {
  display: block;
  margin: 0 0 8rpx;
  color: #626760;
  font-size: 19rpx;
  font-weight: 700;
}

.exercise-default-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr) auto;
  align-items: end;
  gap: 12rpx;
  margin-top: 16rpx;
}

.fitness-input {
  width: 100%;
}

.exercise-numeric-input {
  text-align: center;
}

@media (max-width: 360px) {
  .exercise-default-row {
    grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  }

  .exercise-default-row :deep(button) {
    grid-column: 1 / -1;
  }
}
</style>
