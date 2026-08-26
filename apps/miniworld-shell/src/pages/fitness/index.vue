<script lang="ts" setup>
import type { FitnessPlan } from '@/modules/fitness'
import { useFitnessStore } from '@/modules/fitness'

definePage({ style: { navigationBarTitleText: '健身记录' } })

const store = useFitnessStore()
const error = ref('')

onShow(async () => {
  error.value = ''
  try {
    await store.refreshHome()
  }
  catch {
    error.value = '暂时无法读取训练数据，请确认本地 API 已启动。'
  }
})

function openPlan(plan: FitnessPlan) {
  uni.navigateTo({ url: `/pages/fitness/plan-preview?planId=${plan.id}` })
}

function continueWorkout() {
  if (store.state.activeSession)
    uni.navigateTo({ url: `/pages/fitness/plan?sessionId=${store.state.activeSession.id}` })
}

function openPage(path: 'history' | 'stats' | 'settings') {
  uni.navigateTo({ url: `/pages/fitness/${path}` })
}
</script>

<template>
  <view class="fitness-page pt-safe">
    <view class="fitness-shell">
      <view class="fitness-heading home-heading">
        <view class="fitness-row-between home-heading-top">
          <view>
            <text class="fitness-eyebrow">FITNESS / LOCAL</text>
            <text class="fitness-title">今天练什么？</text>
          </view>
          <view class="home-date">
            <text class="home-date-day">{{ new Date().getDate() }}</text>
            <text class="home-date-label">{{ new Date().toLocaleDateString('zh-CN', { month: 'short' }) }}</text>
          </view>
        </view>
        <text class="fitness-subtitle">选择一个部位开始，训练过程中每一组都会立即保存。</text>
      </view>

      <text v-if="error" class="fitness-error">{{ error }}</text>

      <view v-if="store.state.activeSession" class="fitness-section">
        <view class="fitness-active" @click="continueWorkout">
          <view class="fitness-row-between">
            <view>
              <text class="fitness-eyebrow">继续未结束训练</text>
              <text class="fitness-list-title">{{ store.state.activeSession.planNameSnapshot }}</text>
              <text class="fitness-meta">已完成 {{ store.state.activeSession.totalSetCount }} 组</text>
            </view>
            <text class="fitness-arrow">→</text>
          </view>
        </view>
      </view>

      <view class="fitness-section plan-section">
        <view class="fitness-row-between section-heading-row">
          <view>
            <text class="fitness-section-title">训练部位</text>
            <text class="fitness-meta">按今天的状态自由选择，不要求固定顺序</text>
          </view>
          <text class="fitness-count">{{ store.state.plans.length }} 个</text>
        </view>
        <view
          v-for="plan in store.state.plans"
          :key="plan.id"
          class="plan-card"
          @click="openPlan(plan)"
        >
          <view class="plan-card-index">
            {{ String(plan.sortOrder + 1).padStart(2, '0') }}
          </view>
          <view class="fitness-list-copy">
            <text class="fitness-list-title">{{ plan.name }}</text>
            <text class="fitness-meta">{{ plan.exerciseCount }} 个动作 · 点击查看并选择</text>
          </view>
          <view class="plan-card-action">
            <text class="plan-card-action-label">进入</text>
            <text class="fitness-arrow">↗</text>
          </view>
        </view>
        <text v-if="!store.state.loading && !store.state.plans.length" class="fitness-empty">还没有训练计划。</text>
      </view>

      <view class="fitness-section fitness-row-between">
        <text class="fitness-section-title">记录</text>
        <view class="fitness-row" style="gap: 28rpx;">
          <text class="fitness-link" @click="openPage('history')">历史</text>
          <text class="fitness-link" @click="openPage('stats')">统计</text>
          <text class="fitness-link" @click="openPage('settings')">管理</text>
        </view>
      </view>

      <view v-if="store.state.recentWorkout" class="fitness-section">
        <text class="fitness-section-title">最近训练</text>
        <view class="fitness-row-between" @click="openPage('history')">
          <view>
            <text class="fitness-list-title">{{ store.state.recentWorkout.session.workoutDate }} · {{ store.state.recentWorkout.session.planNameSnapshot }}</text>
            <text class="fitness-meta">{{ store.state.recentWorkout.exerciseCount }} 个动作 · {{ store.state.recentWorkout.setCount }} 组</text>
          </view>
          <text class="fitness-arrow">→</text>
        </view>
      </view>
    </view>
  </view>
</template>

<style scoped lang="scss">
@import '@/modules/fitness/fitness.scss';

.home-heading {
  padding-bottom: 28rpx;
}

.home-heading-top {
  align-items: flex-start;
}

.home-date {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  color: #176b57;
}

.home-date-day {
  font-family: Georgia, serif;
  font-size: 48rpx;
  font-weight: 700;
  line-height: 1;
}

.home-date-label {
  margin-top: 7rpx;
  color: #777a73;
  font-size: 18rpx;
  text-transform: uppercase;
}

.section-heading-row {
  align-items: flex-end;
  margin-bottom: 22rpx;
}

.section-heading-row .fitness-section-title {
  margin-bottom: 4rpx;
}

.fitness-count {
  color: #777a73;
  font-family: Georgia, serif;
  font-size: 20rpx;
}

.plan-card {
  display: flex;
  min-height: 132rpx;
  align-items: center;
  gap: 18rpx;
  padding: 0 18rpx;
  border-top: 1rpx solid #d5d3cc;
  transition:
    background-color 150ms ease,
    transform 150ms ease;
}

.plan-card:last-child {
  border-bottom: 1rpx solid #d5d3cc;
}

.plan-card:active {
  background: #ebe9e2;
  transform: translateX(4rpx);
}

.plan-card-index {
  width: 54rpx;
  color: #176b57;
  font-family: Georgia, serif;
  font-size: 24rpx;
  font-weight: 700;
}

.plan-card-action {
  display: flex;
  align-items: center;
  gap: 8rpx;
  color: #cf533d;
}

.plan-card-action-label {
  color: #777a73;
  font-size: 18rpx;
}
</style>
