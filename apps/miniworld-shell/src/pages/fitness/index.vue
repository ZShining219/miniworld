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

async function start(plan: FitnessPlan) {
  try {
    const session = await store.startSession(plan.id)
    uni.navigateTo({ url: `/pages/fitness/plan?sessionId=${session.id}` })
  }
  catch {
    error.value = '已有其他训练正在进行，请先继续并结束该训练。'
  }
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
      <view class="fitness-heading">
        <text class="fitness-eyebrow">FITNESS / LOCAL</text>
        <text class="fitness-title">今天练什么？</text>
        <text class="fitness-subtitle">选择计划即可开始；每完成一组都会立即保存。</text>
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

      <view class="fitness-section">
        <text class="fitness-section-title">训练计划</text>
        <view
          v-for="plan in store.state.plans"
          :key="plan.id"
          class="fitness-list-row"
          @click="start(plan)"
        >
          <view class="fitness-list-copy">
            <text class="fitness-list-title">{{ plan.name }}</text>
            <text class="fitness-meta">{{ plan.exerciseCount }} 个动作</text>
          </view>
          <text class="fitness-arrow">→</text>
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
</style>
