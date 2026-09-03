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

function updateInput(value: string | number) {
  inputValue.value = String(value)
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
      <wd-button class="stepper-button" type="info" variant="soft" size="large" :aria-label="`减少${label}`" @click="change(-1)">
        −
      </wd-button>
      <view class="stepper-value">
        <wd-input
          v-if="editing"
          class="stepper-input"
          type="digit"
          inputmode="decimal"
          :model-value="inputValue"
          :focus="editing"
          :aria-label="`输入${label}`"
          @update:model-value="updateInput"
          @blur="commitInput"
          @confirm="commitInput"
        />
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
      <wd-button class="stepper-button" type="info" variant="soft" size="large" :aria-label="`增加${label}`" @click="change(1)">
        +
      </wd-button>
      <view v-if="stepOptions.length" class="stepper-options" :aria-label="`${label}增减档位`">
        <wd-button
          v-for="option in stepOptions"
          :key="option"
          class="stepper-option"
          type="primary"
          :variant="option === step ? 'base' : 'soft'"
          size="medium"
          :aria-label="`${label}每次增减${option}`"
          :aria-pressed="option === step"
          :disabled="stepOptionsDisabled"
          @click="emit('update:step', option)"
        >
          {{ option }}
        </wd-button>
      </view>
    </view>
  </view>
</template>

<style scoped lang="scss">
.stepper {
  padding: var(--mw-space-3) 0;
}

.stepper-label {
  display: block;
  margin-bottom: var(--mw-space-2);
  color: var(--mw-color-text-secondary);
  font-size: var(--mw-font-body);
  font-weight: 650;
}

.stepper-control {
  display: grid;
  grid-template-columns: var(--mw-touch-size) minmax(0, 1fr) var(--mw-touch-size);
  align-items: center;
  gap: var(--mw-space-2);
}

.stepper-control-options {
  grid-template-columns: var(--mw-touch-size) minmax(0, 1fr) var(--mw-touch-size);
}

.stepper-button {
  width: var(--mw-touch-size);
  min-width: var(--mw-touch-size);
  padding: 0;
  font-size: var(--mw-font-stepper-control);
}

.stepper-value {
  display: flex;
  min-height: 52px;
  align-items: baseline;
  justify-content: center;
  gap: var(--mw-space-2);
  border: 1px solid var(--mw-color-border-strong);
  border-radius: var(--mw-radius-md);
  background: var(--mw-color-surface);
}

.stepper-number {
  font-size: var(--mw-font-stepper-value);
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}

.stepper-number-editable {
  min-width: 64px;
  padding: var(--mw-space-1) var(--mw-space-2);
  border-bottom: 2px solid var(--mw-color-primary);
  text-align: center;
}

.stepper-input {
  width: 96px;
  max-width: 68%;
  min-height: var(--mw-touch-size);
  box-sizing: border-box;
  padding: 0 var(--mw-space-2);
  border: 0;
  border-bottom: 2px solid var(--mw-color-primary);
  border-radius: 0;
  color: var(--mw-color-text-primary);
  background: transparent;
  font-size: var(--mw-font-stepper-value);
  font-weight: 700;
  text-align: center;
}

.stepper-unit {
  color: var(--mw-color-text-secondary);
  font-size: var(--mw-font-body);
}

.stepper-options {
  display: flex;
  width: 100%;
  grid-column: 1 / -1;
  flex-wrap: wrap;
  min-width: 0;
  gap: var(--mw-space-2);
  padding-top: var(--mw-space-2);
}

.stepper-option {
  min-width: var(--mw-touch-size);
  flex: 1;
}
</style>
