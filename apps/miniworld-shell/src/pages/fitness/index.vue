<script lang="ts" setup>
import type { FitnessPlan } from '@/modules/fitness'
import { useFitnessStore } from '@/modules/fitness'
import FitnessPageShell from '@/modules/fitness/components/FitnessPageShell.vue'
import ReorderablePlanList from '@/modules/fitness/components/ReorderablePlanList.vue'
import FitnessSectionHeader from '@/modules/fitness/components/FitnessSectionHeader.vue'

definePage({ style: { navigationBarTitleText: '健身记录' } })

const store = useFitnessStore()
const error = ref('')
const planList = ref<{ cancelDrag: () => void } | null>(null)

onShow(async () => {
  error.value = ''
  try {
    await store.refreshHome()
  }
  catch {
    error.value = '暂时无法读取训练数据，请确认本地 API 已启动。'
  }
})

onHide(() => planList.value?.cancelDrag())

function openPlan(plan: FitnessPlan) {
  uni.navigateTo({ url: `/pages/fitness/plan-preview?planId=${plan.id}` })
}

async function reorderPlans(ids: string[]) {
  error.value = ''
  try {
    await store.reorderPlans(ids)
  }
  catch {
    error.value = '排序保存失败，已恢复'
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
  <FitnessPageShell
    eyebrow="FITNESS / LOCAL"
    title="今天练什么？"
    subtitle="选择一个部位开始，训练过程中每一组都会立即保存。"
    :error="error"
    compact-heading
  >
    <template #heading>
      <view>
        <view class="fitness-row-between home-heading-top">
          <view>
            <text class="fitness-title">今天练什么？</text>
          </view>
          <view class="home-date">
            <text class="home-date-day">{{ new Date().getDate() }}</text>
            <text class="home-date-label">{{ new Date().toLocaleDateString('zh-CN', { month: 'short' }) }}</text>
          </view>
        </view>
        <text class="fitness-subtitle">选择一个部位开始，训练过程中每一组都会立即保存。</text>
      </view>
    </template>

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
      <FitnessSectionHeader title="训练部位" subtitle="自由选择 · 长按拖动调整" roomy>
        <template #right>
          <text class="fitness-count">{{ store.state.plans.length }} 个</text>
        </template>
      </FitnessSectionHeader>
      <ReorderablePlanList
        ref="planList"
        :plans="store.state.plans"
        :disabled="store.state.reorderingPlans"
        @select="openPlan"
        @reorder="reorderPlans"
      />
      <text v-if="!store.state.loading && !store.state.plans.length" class="fitness-empty">还没有训练计划。</text>
    </view>

    <view class="fitness-section home-record-section">
      <text class="fitness-section-title home-record-title">记录</text>
      <view class="home-record-nav">
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
  </FitnessPageShell>
</template>

<style scoped lang="scss">
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

.fitness-count {
  color: #777a73;
  font-family: Georgia, serif;
  font-size: 20rpx;
}

.home-record-section {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24rpx;
}

.home-record-title {
  flex: 0 0 auto;
  margin-bottom: 0;
}

.home-record-nav {
  display: flex;
  min-width: 0;
  flex: 1 1 auto;
  align-items: center;
  justify-content: flex-end;
  gap: 28rpx;
  white-space: nowrap;
}

@media (max-width: 420px) {
  .home-record-section {
    gap: 16rpx;
  }

  .home-record-nav {
    gap: 20rpx;
  }
}
</style>
