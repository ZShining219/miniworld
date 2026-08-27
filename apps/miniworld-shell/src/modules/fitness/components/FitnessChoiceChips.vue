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
    <button
      v-for="item in items"
      :key="item.id"
      class="fitness-chip"
      :class="{ 'fitness-chip-active': modelValue === item.id }"
      :aria-pressed="modelValue === item.id"
      @click="emit('select', item.id)"
    >
      {{ item.name }}
    </button>
  </view>
</template>
