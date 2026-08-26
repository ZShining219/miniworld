<script setup lang="ts">
const props = withDefaults(defineProps<{
  modelValue: number
  label: string
  unit?: string
  step?: number
  min?: number
}>(), { unit: '', step: 1, min: 0 })

const emit = defineEmits<{ 'update:modelValue': [value: number] }>()

function change(direction: number) {
  const decimals = String(props.step).split('.')[1]?.length || 0
  const value = Math.max(props.min, props.modelValue + direction * props.step)
  emit('update:modelValue', Number(value.toFixed(decimals)))
}
</script>

<template>
  <view class="stepper">
    <text class="stepper-label">{{ label }}</text>
    <view class="stepper-control">
      <button class="stepper-button" :aria-label="`减少${label}`" @click="change(-1)">
        −
      </button>
      <view class="stepper-value">
        <text class="stepper-number">{{ modelValue }}</text>
        <text v-if="unit" class="stepper-unit">{{ unit }}</text>
      </view>
      <button class="stepper-button" :aria-label="`增加${label}`" @click="change(1)">
        +
      </button>
    </view>
  </view>
</template>

<style scoped lang="scss">
.stepper {
  padding: 22rpx 0;
}

.stepper-label {
  display: block;
  margin-bottom: 14rpx;
  color: #6f736c;
  font-size: 21rpx;
}

.stepper-control {
  display: grid;
  grid-template-columns: 96rpx minmax(0, 1fr) 96rpx;
  min-height: 100rpx;
  align-items: stretch;
}

.stepper-button {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  border: 1rpx solid #92958e;
  border-radius: 2rpx;
  color: #1d2420;
  background: #ebeae4;
  font-size: 45rpx;
}

.stepper-value {
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: 10rpx;
  border-top: 1rpx solid #92958e;
  border-bottom: 1rpx solid #92958e;
  background: #fcfbf7;
}

.stepper-number {
  font-family: Georgia, serif;
  font-size: 48rpx;
  font-weight: 700;
}

.stepper-unit {
  color: #6f736c;
  font-size: 21rpx;
}
</style>
