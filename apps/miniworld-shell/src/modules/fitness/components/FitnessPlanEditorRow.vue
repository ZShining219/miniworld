<script setup lang="ts">
import type { FitnessPlan } from '@/modules/fitness'

defineProps<{
  plan: FitnessPlan
  selected: boolean
}>()

const emit = defineEmits<{
  'select': []
  'save': []
  'archive': []
  'update:name': [value: string]
}>()
</script>

<template>
  <view class="plan-editor-row" :class="{ 'plan-editor-row-selected': selected }">
    <view class="plan-editor-field">
      <text class="plan-editor-label">计划名称</text>
      <input
        class="fitness-input"
        :value="plan.name"
        @focus="emit('select')"
        @input="emit('update:name', $event.detail.value)"
      >
    </view>
    <view class="plan-editor-actions">
      <button class="fitness-secondary" @click="emit('save')">
        保存
      </button>
      <button class="fitness-danger" @click="emit('archive')">
        归档
      </button>
    </view>
  </view>
</template>

<style scoped lang="scss">
.plan-editor-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 12rpx;
  padding: 22rpx 0;
  border-top: 1rpx solid #d5d3cc;
}

.plan-editor-row-selected {
  border-left: 5rpx solid #176b57;
  padding-left: 16rpx;
}

.plan-editor-label {
  display: block;
  margin-bottom: 8rpx;
  color: #626760;
  font-size: 19rpx;
  font-weight: 700;
}

.plan-editor-actions {
  display: flex;
  align-items: end;
  gap: 10rpx;
}

.plan-editor-actions button {
  padding: 0 18rpx;
}

@media (max-width: 360px) {
  .plan-editor-row {
    grid-template-columns: minmax(0, 1fr);
  }
}
</style>
