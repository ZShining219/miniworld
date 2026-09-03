<script setup lang="ts">
interface ChoiceItem {
  id: string
  name: string
}

defineProps<{
  items: ChoiceItem[]
  modelValue: string
  label: string
}>()

const emit = defineEmits<{ select: [id: string] }>()
</script>

<template>
  <view class="fitness-chip-list" role="group" :aria-label="label">
    <wd-button
      v-for="item in items"
      :key="item.id"
      class="fitness-chip"
      type="primary"
      :variant="modelValue === item.id ? 'base' : 'soft'"
      size="medium"
      :aria-pressed="modelValue === item.id"
      @click="emit('select', item.id)"
    >
      {{ item.name }}
    </wd-button>
  </view>
</template>
