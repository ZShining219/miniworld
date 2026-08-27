<script setup lang="ts">
withDefaults(defineProps<{
  title: string
  subtitle?: string
  roomy?: boolean
}>(), { subtitle: '', roomy: false })
</script>

<template>
  <view class="fitness-section-heading" :class="{ 'fitness-section-heading-roomy': roomy }">
    <view class="fitness-section-heading-copy">
      <text class="fitness-section-title">{{ title }}</text>
      <text v-if="subtitle" class="fitness-meta">{{ subtitle }}</text>
    </view>
    <slot name="right" />
  </view>
</template>

<style scoped lang="scss">
.fitness-section-heading {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 20rpx;
  margin-bottom: 18rpx;
}

.fitness-section-heading-roomy {
  margin-bottom: 22rpx;
}

.fitness-section-heading-copy {
  min-width: 0;
  flex: 1;
}

.fitness-section-title {
  margin-bottom: 4rpx;
}
</style>
