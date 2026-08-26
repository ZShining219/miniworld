<script lang="ts" setup>
import type { HistoryItem } from '@/modules/fitness'
import { fitnessApi } from '@/modules/fitness'

definePage({ style: { navigationBarTitleText: '训练历史' } })

const items = ref<HistoryItem[]>([])
const loading = ref(true)
const error = ref('')

onShow(async () => {
  loading.value = true
  try {
    items.value = await fitnessApi.history()
  }
  catch {
    error.value = '暂时无法读取训练历史。'
  }
  finally {
    loading.value = false
  }
})

function duration(seconds: number) {
  const minutes = Math.max(1, Math.round(seconds / 60))
  return minutes < 60 ? `${minutes} 分钟` : `${Math.floor(minutes / 60)} 小时 ${minutes % 60} 分钟`
}
</script>

<template>
  <view class="fitness-page pt-safe">
    <view class="fitness-shell">
      <view class="fitness-heading">
        <text class="fitness-eyebrow">FITNESS HISTORY</text>
        <text class="fitness-title">训练历史</text>
        <text class="fitness-subtitle">这里只统计已经结束的训练。</text>
      </view>
      <text v-if="error" class="fitness-error">{{ error }}</text>
      <text v-if="loading" class="fitness-empty">正在读取…</text>
      <text v-else-if="!items.length" class="fitness-empty">完成第一次训练后，记录会出现在这里。</text>

      <view v-for="item in items" :key="item.session.id" class="history-session">
        <view class="fitness-row-between history-heading">
          <view>
            <text class="history-date">{{ item.session.workoutDate }}</text>
            <text class="fitness-list-title">{{ item.session.planNameSnapshot }}</text>
          </view>
          <text class="fitness-meta">{{ duration(item.durationSeconds) }}</text>
        </view>
        <view class="history-summary">
          <text>{{ item.exerciseCount }} 个动作</text>
          <text>{{ item.setCount }} 组</text>
        </view>
        <view v-for="exercise in item.exercises" :key="exercise.exerciseId" class="history-exercise">
          <text class="fitness-list-title">{{ exercise.exerciseName }}</text>
          <text v-for="set in exercise.sets" :key="set.id" class="history-set">{{ set.weight }} kg × {{ set.reps }}</text>
        </view>
      </view>
    </view>
  </view>
</template>

<style scoped lang="scss">
@import '@/modules/fitness/fitness.scss';

.history-session {
  padding: 38rpx 0;
  border-bottom: 2rpx solid #1d2420;
}

.history-heading {
  align-items: flex-start;
}

.history-date {
  display: block;
  margin-bottom: 10rpx;
  color: #cf533d;
  font-family: Georgia, serif;
  font-size: 21rpx;
  font-weight: 700;
}

.history-summary {
  display: flex;
  gap: 24rpx;
  margin: 20rpx 0 28rpx;
  color: #777a73;
  font-size: 20rpx;
}

.history-exercise {
  padding: 22rpx 0;
  border-top: 1rpx solid #d5d3cc;
}

.history-set {
  display: block;
  margin-top: 9rpx;
  color: #555a54;
  font-size: 23rpx;
}
</style>
