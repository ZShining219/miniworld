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
      <wd-input
        class="fitness-input"
        :model-value="plan.name"
        clearable
        @focus="emit('select')"
        @update:model-value="emit('update:name', String($event))"
      />
    </view>
    <view class="plan-editor-actions">
      <wd-button class="fitness-secondary" type="primary" variant="soft" size="medium" @click="emit('save')">
        保存
      </wd-button>
      <wd-button class="fitness-danger" type="danger" variant="text" size="medium" @click="emit('archive')">
        归档
      </wd-button>
    </view>
  </view>
</template>

<style scoped lang="scss">
.plan-editor-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: var(--mw-space-3);
  padding: var(--mw-space-4) 0;
  border-top: 1px solid var(--mw-color-border);
}

.plan-editor-row-selected {
  padding-left: var(--mw-space-3);
  border-left: 4px solid var(--mw-color-primary);
}

.plan-editor-label {
  display: block;
  margin-bottom: var(--mw-space-2);
  color: var(--mw-color-text-secondary);
  font-size: var(--mw-font-body);
  font-weight: 700;
}

.plan-editor-actions {
  display: flex;
  align-items: end;
  gap: var(--mw-space-2);
}

@media (max-width: 430px) {
  .plan-editor-row {
    grid-template-columns: minmax(0, 1fr);
  }

  .plan-editor-actions {
    justify-content: flex-end;
  }
}
</style>
