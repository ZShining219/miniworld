<script lang="ts" setup>
defineProps<{
  index: string
  title: string
  caption: string
  description: string
}>()
</script>

<template>
  <view class="module-page pt-safe">
    <view class="module-header">
      <text class="module-index">{{ index }}</text>
      <text class="module-caption">{{ caption }}</text>
    </view>
    <view class="module-body">
      <text class="module-title">{{ title }}</text>
      <text class="module-description">{{ description }}</text>
      <view class="pending-line">
        <view class="pending-mark" />
        <text>MODULE NOT CONNECTED</text>
      </view>
    </view>
    <view class="boundary-note">
      <text>独立工作流</text>
      <text>本地数据</text>
      <text>显式授权</text>
    </view>
  </view>
</template>

<style scoped lang="scss">
.module-page {
  min-height: 100vh;
  box-sizing: border-box;
  padding: 34rpx 32rpx 150rpx;
  color: #1d2420;
  background: #f4f3ee;
  font-family: "PingFang SC", "Noto Sans CJK SC", sans-serif;
}

.module-header,
.pending-line,
.boundary-note {
  display: flex;
  align-items: center;
}

.module-header {
  justify-content: space-between;
  padding-bottom: 26rpx;
  border-bottom: 2rpx solid #1d2420;
}

.module-index {
  font-family: Georgia, serif;
  font-size: 28rpx;
  font-weight: 700;
}

.module-caption {
  color: #cf533d;
  font-size: 19rpx;
  font-weight: 700;
}

.module-body {
  max-width: 900rpx;
  padding: 100rpx 0 82rpx;
}

.module-title,
.module-description {
  display: block;
}

.module-title {
  font-family: "Songti SC", "Noto Serif CJK SC", serif;
  font-size: 64rpx;
  font-weight: 700;
}

.module-description {
  max-width: 720rpx;
  margin-top: 28rpx;
  color: #646861;
  font-size: 27rpx;
  line-height: 1.75;
}

.pending-line {
  gap: 16rpx;
  margin-top: 62rpx;
  color: #176b57;
  font-size: 19rpx;
  font-weight: 700;
}

.pending-mark {
  width: 36rpx;
  height: 4rpx;
  background: #176b57;
}

.boundary-note {
  flex-wrap: wrap;
  gap: 18rpx 34rpx;
  padding-top: 28rpx;
  border-top: 1rpx solid #c9c8c1;
  color: #777a73;
  font-size: 19rpx;
}

@media (min-width: 900px) {
  .module-page {
    padding: 48px max(48px, calc((100vw - 1180px) / 2)) 130px;
  }

  .module-body {
    padding: 120px 0 110px;
  }

  .module-title {
    font-size: 68px;
  }
}
</style>
