<script lang="ts" setup>
import type { MiniWorldModule } from '@/modules/registry'
import { moduleRegistry } from '@/modules/registry'

defineOptions({
  name: 'Home',
})
definePage({
  // 使用 type: "home" 属性设置首页，其他页面不需要设置，默认为page
  type: 'home',
  style: {
    // 'custom' 表示开启自定义导航栏，默认 'default'
    navigationStyle: 'custom',
    navigationBarTitleText: 'MiniWorld',
  },
})

const modules = moduleRegistry

function openModule(module: MiniWorldModule) {
  if (module.navigation === 'tab') {
    uni.switchTab({ url: module.path })
    return
  }
  uni.navigateTo({ url: module.path })
}
</script>

<template>
  <view class="shell-page pt-safe">
    <view class="masthead">
      <view>
        <text class="wordmark">MINIWORLD</text>
        <text class="edition">LOCAL EDITION / 01</text>
      </view>
      <view class="local-status">
        <view class="status-dot" />
        <text>LOCAL</text>
      </view>
    </view>

    <view class="intro">
      <text class="eyebrow">PERSONAL AGENT WORKSPACE</text>
      <text class="headline">把工作与成长，放回自己的世界。</text>
      <text class="summary">统一入口已经就绪。现有 Demo 将以独立工具接入，数据和权限仍保留在各自边界内。</text>
    </view>

    <view class="module-list">
      <view
        v-for="module in modules"
        :key="module.key"
        class="module-row"
        @click="openModule(module)"
      >
        <text class="module-number">{{ module.key }}</text>
        <view class="module-copy">
          <text class="module-title">{{ module.title }}</text>
          <text class="module-caption">{{ module.caption }}</text>
        </view>
        <text class="module-state">{{ module.state }}</text>
        <text class="module-arrow">→</text>
      </view>
    </view>

    <view class="system-footnote">
      <text>WEB READY</text>
      <text>ANDROID RESERVED</text>
      <text>PRIVATE BY DEFAULT</text>
    </view>
  </view>
</template>

<style scoped lang="scss">
.shell-page {
  min-height: 100vh;
  box-sizing: border-box;
  padding: 30rpx 32rpx 150rpx;
  color: #1d2420;
  background: #f4f3ee;
  font-family: 'PingFang SC', 'Noto Sans CJK SC', sans-serif;
}

.masthead,
.local-status,
.module-row,
.system-footnote {
  display: flex;
  align-items: center;
}

.masthead {
  justify-content: space-between;
  padding-bottom: 28rpx;
  border-bottom: 2rpx solid #1d2420;
}

.wordmark,
.edition,
.eyebrow,
.module-caption,
.module-state,
.system-footnote {
  letter-spacing: 0;
}

.wordmark {
  display: block;
  font-family: Georgia, serif;
  font-size: 34rpx;
  font-weight: 700;
}

.edition {
  display: block;
  margin-top: 5rpx;
  color: #72746d;
  font-size: 18rpx;
}

.local-status {
  gap: 10rpx;
  color: #176b57;
  font-size: 20rpx;
  font-weight: 700;
}

.status-dot {
  width: 12rpx;
  height: 12rpx;
  border-radius: 50%;
  background: #21a47e;
  box-shadow: 0 0 0 7rpx rgba(33, 164, 126, 0.12);
}

.intro {
  max-width: 1040rpx;
  padding: 82rpx 0 68rpx;
}

.eyebrow {
  display: block;
  color: #cf533d;
  font-size: 20rpx;
  font-weight: 700;
}

.headline {
  display: block;
  max-width: 920rpx;
  margin-top: 22rpx;
  font-family: 'Songti SC', 'Noto Serif CJK SC', serif;
  font-size: 58rpx;
  font-weight: 700;
  line-height: 1.24;
}

.summary {
  display: block;
  max-width: 800rpx;
  margin-top: 28rpx;
  color: #626760;
  font-size: 26rpx;
  line-height: 1.75;
}

.module-list {
  border-top: 2rpx solid #1d2420;
}

.module-row {
  min-height: 132rpx;
  border-bottom: 1rpx solid #c9c8c1;
  transition: background-color 150ms ease;
}

.module-row:active {
  background: #ebe9e2;
}

.module-number {
  width: 64rpx;
  color: #989991;
  font-family: Georgia, serif;
  font-size: 22rpx;
}

.module-copy {
  flex: 1;
}

.module-title,
.module-caption {
  display: block;
}

.module-title {
  font-family: 'Songti SC', serif;
  font-size: 34rpx;
  font-weight: 700;
}

.module-caption {
  margin-top: 5rpx;
  color: #7b7d76;
  font-size: 19rpx;
  text-transform: uppercase;
}

.module-state {
  margin-right: 24rpx;
  padding: 8rpx 14rpx;
  border: 1rpx solid #bdbdb6;
  color: #656861;
  font-size: 18rpx;
}

.module-arrow {
  color: #cf533d;
  font-size: 34rpx;
}

.system-footnote {
  flex-wrap: wrap;
  gap: 18rpx 32rpx;
  padding-top: 34rpx;
  color: #777a73;
  font-size: 17rpx;
  font-weight: 600;
}

@media (min-width: 900px) {
  .shell-page {
    padding: 48px max(48px, calc((100vw - 1180px) / 2)) 130px;
  }

  .intro {
    padding: 92px 0 78px;
  }

  .headline {
    font-size: 64px;
  }

  .module-row {
    min-height: 104px;
  }
}
</style>
