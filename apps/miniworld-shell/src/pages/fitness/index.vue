<script lang="ts" setup>
import type { FitnessPlan } from '@/modules/fitness'
import { useFitnessStore, useFitnessWorkoutStatus } from '@/modules/fitness'
import FitnessPageShell from '@/modules/fitness/components/FitnessPageShell.vue'
import ReorderablePlanList from '@/modules/fitness/components/ReorderablePlanList.vue'
import FitnessSectionHeader from '@/modules/fitness/components/FitnessSectionHeader.vue'

definePage({ style: { navigationBarTitleText: '健身记录' } })

const store = useFitnessStore()
const error = ref('')
const planList = ref<{ cancelDrag: () => void } | null>(null)
const { workoutStatus, workoutActionLabel, handleWorkoutAction } = useFitnessWorkoutStatus('index', false)

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

function openPage(path: 'history' | 'stats' | 'settings') {
  uni.navigateTo({ url: `/pages/fitness/${path}` })
}
</script>

<template>
  <FitnessPageShell
    eyebrow="本地训练记录"
    title="今天练什么？"
    subtitle="选择一个部位开始，训练过程中每一组都会立即保存。"
    :error="error"
    compact-heading
    :workout-status="workoutStatus"
    :workout-action-label="workoutActionLabel"
    @workout-action="handleWorkoutAction"
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
        <text class="fitness-subtitle">选择训练部位；每完成一组，就立即保存一组。</text>
      </view>
    </template>

    <view class="fitness-section plan-section">
      <FitnessSectionHeader title="训练部位" subtitle="自由选择 · 长按拖动调整" roomy>
        <template #right>
          <text class="fitness-count">{{ store.state.plans.length }} 个</text>
        </template>
      </FitnessSectionHeader>
      <view v-if="store.state.loading" class="fitness-loading-state">
        <wd-loading size="22px" />
        <text class="fitness-meta">正在读取训练计划</text>
      </view>
      <ReorderablePlanList
        v-else-if="store.state.plans.length"
        ref="planList"
        :plans="store.state.plans"
        :disabled="store.state.reorderingPlans"
        @select="openPlan"
        @reorder="reorderPlans"
      />
      <view v-else class="fitness-empty-state">
        <wd-empty tip="还没有训练计划" icon-size="64" />
        <wd-button type="primary" variant="soft" size="large" block @click="openPage('settings')">
          创建训练计划
        </wd-button>
      </view>
    </view>

    <view class="fitness-section home-record-section">
      <view>
        <text class="fitness-section-title home-record-title">训练记录</text>
        <text class="fitness-meta">回顾完成情况和重量变化</text>
      </view>
      <view class="home-record-nav">
        <wd-button type="primary" variant="text" size="medium" @click="openPage('history')">
          历史
        </wd-button>
        <wd-button type="primary" variant="text" size="medium" @click="openPage('stats')">
          统计
        </wd-button>
        <wd-button type="primary" variant="text" size="medium" @click="openPage('settings')">
          管理
        </wd-button>
      </view>
    </view>

    <view v-if="store.state.recentWorkout" class="fitness-section">
      <text class="fitness-section-title">最近训练</text>
      <view class="fitness-row-between recent-workout" role="button" aria-label="查看最近训练" @click="openPage('history')">
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
  color: var(--mw-color-primary);
}

.home-date-day {
  font-size: var(--mw-font-data);
  font-weight: 700;
  line-height: 1;
}

.home-date-label {
  margin-top: var(--mw-space-1);
  color: var(--mw-color-text-muted);
  font-size: var(--mw-font-auxiliary);
}

.fitness-count {
  color: var(--mw-color-text-muted);
  font-size: var(--mw-font-body);
}

.home-record-section {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--mw-space-4);
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
  gap: var(--mw-space-1);
  white-space: nowrap;
}

@media (max-width: 430px) {
  .home-record-section {
    align-items: flex-start;
    gap: var(--mw-space-3);
  }

  .home-record-nav {
    flex-wrap: wrap;
    gap: 0;
  }
}

.recent-workout {
  min-height: var(--mw-touch-size);
}
</style>
