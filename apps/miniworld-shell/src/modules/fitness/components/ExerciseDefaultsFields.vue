<script setup lang="ts">
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

function numberValue(input: string | number): number {
  const value = Number(input)
  return Number.isFinite(value) ? value : 0
}
</script>

<template>
  <view class="exercise-default-fields">
    <view class="exercise-default-name">
      <text class="exercise-field-label">动作名称</text>
      <wd-input
        class="fitness-input"
        :model-value="name"
        :placeholder="namePlaceholder"
        clearable
        @update:model-value="emit('update:name', String($event))"
      />
    </view>
    <view class="exercise-default-row">
      <view class="exercise-default-field">
        <text class="exercise-field-label">默认重量（kg）</text>
        <wd-input
          class="fitness-input exercise-numeric-input"
          type="digit"
          inputmode="decimal"
          :model-value="String(weight)"
          @update:model-value="emit('update:weight', numberValue($event))"
        />
      </view>
      <view class="exercise-default-field">
        <text class="exercise-field-label">默认次数（次）</text>
        <wd-input
          class="fitness-input exercise-numeric-input"
          type="number"
          inputmode="numeric"
          :model-value="String(reps)"
          @update:model-value="emit('update:reps', numberValue($event))"
        />
      </view>
    </view>
    <view v-if="$slots.action" class="exercise-default-action">
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
  margin: 0 0 var(--mw-space-2);
  color: var(--mw-color-text-secondary);
  font-size: var(--mw-font-body);
  font-weight: 700;
}

.exercise-default-row {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  align-items: end;
  gap: var(--mw-space-3);
  margin-top: var(--mw-space-4);
}

.fitness-input {
  width: 100%;
}

.exercise-numeric-input {
  text-align: center;
}

.exercise-default-action {
  display: grid;
  margin-top: var(--mw-space-4);
}
</style>
