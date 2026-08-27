<script setup lang="ts">
import { ref } from 'vue'

const props = withDefaults(defineProps<{
  modelValue: number
  label: string
  unit?: string
  step?: number
  min?: number
  max?: number
  editable?: boolean
  stepOptions?: number[]
  stepOptionsDisabled?: boolean
}>(), { unit: '', step: 1, min: 0, max: Number.MAX_SAFE_INTEGER, editable: false, stepOptions: () => [], stepOptionsDisabled: false })

const emit = defineEmits<{
  'update:modelValue': [value: number]
  'update:step': [value: number]
}>()

const editing = ref(false)
const inputValue = ref('')

function normalize(value: number) {
  const clamped = Math.min(props.max, Math.max(props.min, value))
  return Math.round(clamped * 100) / 100
}

function change(direction: number) {
  if (editing.value)
    commitInput()
  const scaledValue = Math.round(props.modelValue * 100)
  const scaledStep = Math.round(props.step * 100)
  emit('update:modelValue', normalize((scaledValue + direction * scaledStep) / 100))
}

function startEditing() {
  if (!props.editable)
    return
  inputValue.value = String(props.modelValue)
  editing.value = true
}

function updateInput(event: { detail: { value: string } }) {
  inputValue.value = event.detail.value
}

function commitInput() {
  if (!editing.value)
    return
  const trimmed = inputValue.value.trim()
  const value = Number(trimmed)
  editing.value = false
  const decimalPattern = /^(?:\d+\.?\d{0,2}|\.\d{1,2})$/
  if (!decimalPattern.test(trimmed) || !Number.isFinite(value) || value < props.min || value > props.max)
    return
  emit('update:modelValue', normalize(value))
}
</script>

<template>
  <view class="stepper">
    <text class="stepper-label">{{ label }}</text>
    <view class="stepper-control" :class="{ 'stepper-control-options': stepOptions.length }">
      <button class="stepper-button" :aria-label="`减少${label}`" @click="change(-1)">
        −
      </button>
      <view class="stepper-value">
        <input
          v-if="editing"
          class="stepper-input"
          type="digit"
          :value="inputValue"
          :focus="editing"
          :aria-label="`输入${label}`"
          @input="updateInput"
          @blur="commitInput"
          @confirm="commitInput"
        >
        <text
          v-else
          class="stepper-number"
          :class="{ 'stepper-number-editable': editable }"
          :role="editable ? 'button' : undefined"
          :aria-label="editable ? `手动输入${label}` : undefined"
          @click="startEditing"
        >
          {{ modelValue }}
        </text>
        <text v-if="unit" class="stepper-unit">{{ unit }}</text>
      </view>
      <button class="stepper-button" :aria-label="`增加${label}`" @click="change(1)">
        +
      </button>
      <view v-if="stepOptions.length" class="stepper-options" :aria-label="`${label}增减档位`">
        <button
          v-for="option in stepOptions"
          :key="option"
          class="stepper-option"
          :class="{ 'stepper-option-active': option === step }"
          :aria-label="`${label}每次增减${option}`"
          :aria-pressed="option === step"
          :disabled="stepOptionsDisabled"
          @click="emit('update:step', option)"
        >
          {{ option }}
        </button>
      </view>
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

.stepper-control-options {
  grid-template-columns: 96rpx minmax(0, 1fr) 96rpx 88rpx;
  min-height: 336rpx;
}

.stepper-button {
  display: flex;
  width: 100%;
  height: 100%;
  box-sizing: border-box;
  align-items: center;
  justify-content: center;
  margin: 0;
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

.stepper-number-editable {
  min-width: 96rpx;
  padding: 8rpx 10rpx 6rpx;
  border-bottom: 2rpx solid #176b57;
  text-align: center;
}

.stepper-input {
  width: 176rpx;
  max-width: 70%;
  height: 76rpx;
  box-sizing: border-box;
  padding: 0 8rpx;
  border: 0;
  border-bottom: 2rpx solid #176b57;
  color: #1d2420;
  background: transparent;
  font-family: Georgia, serif;
  font-size: 48rpx;
  font-weight: 700;
  line-height: 76rpx;
  text-align: center;
}

.stepper-unit {
  color: #6f736c;
  font-size: 21rpx;
}

.stepper-options {
  display: grid;
  width: 100%;
  height: 100%;
  grid-template-rows: repeat(4, minmax(0, 1fr));
  min-width: 0;
}

.stepper-option {
  display: flex;
  width: 100%;
  height: 100%;
  min-width: 0;
  min-height: 84rpx;
  box-sizing: border-box;
  align-items: center;
  justify-content: center;
  margin: 0;
  padding: 0;
  border: 1rpx solid #92958e;
  border-left: 0;
  border-radius: 0;
  color: #555a54;
  background: #ebeae4;
  font-size: 20rpx;
  line-height: 82rpx;
}

.stepper-option + .stepper-option {
  border-top: 0;
}

.stepper-option-active {
  color: #fff;
  background: #176b57;
  font-weight: 700;
}
</style>
