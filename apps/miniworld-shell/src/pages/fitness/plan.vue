<script lang="ts" setup>
import type { SessionDetail } from '@/modules/fitness'
import { useFitnessStore } from '@/modules/fitness'

definePage({ style: { navigationBarTitleText: '本次训练' } })

const store = useFitnessStore()
const sessionId = ref('')
const session = ref<SessionDetail | null>(null)
const error = ref('')
const finishing = ref(false)

onLoad((query) => {
  sessionId.value = String(query?.sessionId || '')
})

onShow(() => load())

async function load() {
  if (!sessionId.value)
    return
  try {
    session.value = await store.loadSession(sessionId.value)
  }
  catch {
    error.value = '无法读取本次训练。'
  }
}

function openExercise(exerciseId: string) {
  uni.navigateTo({ url: `/pages/fitness/exercise?sessionId=${sessionId.value}&exerciseId=${exerciseId}` })
}

function requestFinish() {
  uni.showModal({
    title: '结束本次训练',
    content: '已完成的组会进入历史和统计。',
    confirmText: '结束训练',
    success: async (result) => {
      if (!result.confirm || finishing.value)
        return
      finishing.value = true
      try {
        await store.finishSession(sessionId.value)
        uni.redirectTo({ url: '/pages/fitness/history' })
      }
      finally {
        finishing.value = false
      }
    },
  })
}
</script>

<template>
  <view class="fitness-page pt-safe">
    <view class="fitness-shell">
      <view class="fitness-heading">
        <text class="fitness-eyebrow">ACTIVE WORKOUT</text>
        <text class="fitness-title">{{ session?.planNameSnapshot || '训练' }}</text>
        <text class="fitness-subtitle">已完成 {{ session?.totalSetCount || 0 }} 组。选择动作继续记录。</text>
      </view>
      <text v-if="error" class="fitness-error">{{ error }}</text>

      <view class="fitness-section">
        <text class="fitness-section-title">动作</text>
        <view
          v-for="item in session?.exercises || []"
          :key="item.exercise.id"
          class="fitness-list-row"
          @click="openExercise(item.exercise.id)"
        >
          <view class="fitness-list-copy">
            <text class="fitness-list-title">{{ item.exercise.name }}</text>
            <text class="fitness-meta">今天 {{ item.completedSetCount }} 组</text>
          </view>
          <text class="fitness-arrow">→</text>
        </view>
        <text v-if="session && !session.exercises.length" class="fitness-empty">该计划还没有动作，请先到管理页添加。</text>
      </view>

      <view class="fitness-section">
        <button class="fitness-danger" :disabled="finishing" @click="requestFinish">
          {{ finishing ? '正在结束…' : '结束本次训练' }}
        </button>
      </view>
    </view>
  </view>
</template>

<style scoped lang="scss">
@import '@/modules/fitness/fitness.scss';
</style>
