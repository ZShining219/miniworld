<script setup lang="ts">
withDefaults(defineProps<{
  eyebrow: string
  title: string
  subtitle?: string
  error?: string
  compactHeading?: boolean
}>(), {
  subtitle: '',
  error: '',
  compactHeading: false,
})
</script>

<template>
  <view class="fitness-page pt-safe">
    <view class="fitness-shell">
      <view class="fitness-heading" :class="{ 'fitness-heading-compact': compactHeading }">
        <text class="fitness-eyebrow">{{ eyebrow }}</text>
        <slot name="heading">
          <text class="fitness-title">{{ title }}</text>
          <text v-if="subtitle" class="fitness-subtitle">{{ subtitle }}</text>
        </slot>
      </view>
      <text v-if="error" class="fitness-error" role="alert">{{ error }}</text>
      <slot />
    </view>
  </view>
</template>

<style lang="scss">
@import '@/modules/fitness/fitness.scss';
</style>

<style scoped lang="scss">
.fitness-heading-compact {
  padding-bottom: 28rpx;
}
</style>
