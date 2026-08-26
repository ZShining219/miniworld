<script lang="ts" setup>
import type { SessionDetail } from '@/modules/fitness'
import { fitnessApi, useFitnessStore } from '@/modules/fitness'

definePage({ style: { navigationBarTitleText: '本次训练' } })

const store = useFitnessStore()
const sessionId = ref('')
const session = ref<SessionDetail | null>(null)
const error = ref('')
const finishing = ref(false)
const managing = ref(false)
const adding = ref(false)
const newExerciseName = ref('')
const newExerciseWeight = ref(0)
const newExerciseReps = ref(8)

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

async function addExercise() {
  const name = newExerciseName.value.trim()
  if (!name || !session.value || adding.value)
    return
  adding.value = true
  error.value = ''
  try {
    await fitnessApi.createExercise({
      planId: session.value.planId,
      name,
      defaultWeight: newExerciseWeight.value,
      defaultReps: newExerciseReps.value,
    })
    newExerciseName.value = ''
    await load()
  }
  catch {
    error.value = '动作没有添加成功，请稍后重试。'
  }
  finally {
    adding.value = false
  }
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
      <view class="fitness-heading active-heading">
        <text class="fitness-eyebrow">ACTIVE WORKOUT</text>
        <text class="fitness-title">{{ session?.planNameSnapshot || '训练' }}</text>
        <view class="fitness-row-between active-heading-meta">
          <text class="fitness-subtitle">已完成 {{ session?.totalSetCount || 0 }} 组。可按任意顺序选择动作。</text>
          <text class="active-progress">{{ session?.totalSetCount || 0 }}<text class="active-progress-unit">组</text></text>
        </view>
      </view>
      <text v-if="error" class="fitness-error">{{ error }}</text>

      <view class="fitness-section active-exercises-section">
        <view class="fitness-row-between section-heading-row">
          <view>
            <text class="fitness-section-title">本次动作</text>
            <text class="fitness-meta">选择任意动作继续，不要求按列表顺序</text>
          </view>
          <button class="manage-toggle" @click="managing = !managing">
            {{ managing ? '收起' : '管理' }}
          </button>
        </view>
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
          <view class="active-row-actions">
            <text class="fitness-arrow">→</text>
          </view>
        </view>
        <text v-if="session && !session.exercises.length" class="fitness-empty">该计划还没有动作，先添加一个再继续。</text>
        <view v-if="managing" class="active-add-panel">
          <text class="active-add-title">增加动作</text>
          <text class="active-field-label">动作名称</text>
          <input v-model="newExerciseName" class="fitness-input" placeholder="例如：绳索下压">
          <view class="active-add-fields">
            <view>
              <text class="active-field-label">默认重量（kg）</text>
              <input v-model.number="newExerciseWeight" class="fitness-input" type="digit" placeholder="0">
            </view>
            <view>
              <text class="active-field-label">默认次数（次）</text>
              <input v-model.number="newExerciseReps" class="fitness-input" type="number" placeholder="8">
            </view>
            <button class="fitness-secondary" :disabled="adding" @click="addExercise">
              {{ adding ? '添加中' : '添加' }}
            </button>
          </view>
          <text class="active-safe-note">训练中的动作只支持追加，不会从计划或历史记录中删除。</text>
        </view>
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

.active-heading {
  padding-bottom: 28rpx;
}

.active-heading-meta {
  align-items: flex-end;
  gap: 16rpx;
}

.active-heading-meta .fitness-subtitle {
  flex: 1;
}

.active-progress {
  flex: none;
  color: #176b57;
  font-family: Georgia, serif;
  font-size: 48rpx;
  font-weight: 700;
  line-height: 1;
}

.active-progress-unit {
  margin-left: 4rpx;
  color: #777a73;
  font-family: 'PingFang SC', sans-serif;
  font-size: 18rpx;
  font-weight: 400;
}

.active-exercises-section {
  padding-top: 32rpx;
}

.section-heading-row {
  align-items: flex-end;
  margin-bottom: 18rpx;
}

.section-heading-row .fitness-section-title {
  margin-bottom: 4rpx;
}

.manage-toggle {
  min-height: 54rpx;
  padding: 0 18rpx;
  border: 1rpx solid #aaa9a2;
  border-radius: 2rpx;
  color: #176b57;
  background: transparent;
  font-size: 20rpx;
  line-height: 52rpx;
}

.active-row-actions {
  display: flex;
  align-items: center;
}

.active-remove {
  width: 58rpx;
  height: 58rpx;
  padding: 0;
  border: 1rpx solid #d5b2a9;
  border-radius: 50%;
  color: #a43f2e;
  background: transparent;
  font-size: 32rpx;
  line-height: 54rpx;
}

.active-add-panel {
  margin-top: 24rpx;
  padding: 22rpx;
  border: 1rpx solid #c8c8c0;
  background: #ebece6;
}

.active-add-title {
  display: block;
  margin-bottom: 14rpx;
  color: #1d2420;
  font-size: 23rpx;
  font-weight: 700;
}

.active-field-label {
  display: block;
  margin: 0 0 8rpx;
  color: #626760;
  font-size: 19rpx;
  font-weight: 700;
}

.active-add-fields {
  display: grid;
  grid-template-columns: 1fr 1fr auto;
  align-items: end;
  gap: 12rpx;
  margin-top: 12rpx;
}

.active-safe-note {
  display: block;
  margin-top: 16rpx;
  color: #777a73;
  font-size: 18rpx;
  line-height: 1.5;
}
</style>
