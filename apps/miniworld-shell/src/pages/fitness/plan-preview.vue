<script lang="ts" setup>
import type { FitnessExercise, FitnessPlan } from '@/modules/fitness'
import { fitnessApi, useFitnessStore } from '@/modules/fitness'

definePage({ style: { navigationBarTitleText: '训练部位' } })

const store = useFitnessStore()
const planId = ref('')
const plan = ref<FitnessPlan | null>(null)
const exercises = ref<FitnessExercise[]>([])
const newExerciseName = ref('')
const newExerciseWeight = ref(0)
const newExerciseReps = ref(8)
const loading = ref(true)
const saving = ref(false)
const error = ref('')

onLoad((query) => {
  planId.value = String(query?.planId || '')
  load()
})

async function load() {
  if (!planId.value)
    return
  loading.value = true
  try {
    const plans = await fitnessApi.listPlans()
    plan.value = plans.find(item => item.id === planId.value) || null
    exercises.value = await fitnessApi.listExercises(planId.value)
  }
  catch {
    error.value = '暂时无法读取这个训练部位。'
  }
  finally {
    loading.value = false
  }
}

async function startWorkout() {
  if (!plan.value || saving.value)
    return
  saving.value = true
  error.value = ''
  try {
    const session = await store.startSession(plan.value.id)
    uni.redirectTo({ url: `/pages/fitness/plan?sessionId=${session.id}` })
  }
  catch {
    error.value = '已有其他训练正在进行，请先继续并结束该训练。'
  }
  finally {
    saving.value = false
  }
}

async function startExercise(exercise: FitnessExercise) {
  if (!plan.value || saving.value)
    return
  saving.value = true
  error.value = ''
  try {
    const session = await store.startSession(plan.value.id)
    uni.redirectTo({ url: `/pages/fitness/exercise?sessionId=${session.id}&exerciseId=${exercise.id}` })
  }
  catch {
    error.value = '已有其他训练正在进行，请先继续并结束该训练。'
  }
  finally {
    saving.value = false
  }
}

async function addExercise() {
  const name = newExerciseName.value.trim()
  if (!name || !planId.value || saving.value)
    return
  saving.value = true
  try {
    await fitnessApi.createExercise({
      planId: planId.value,
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
    saving.value = false
  }
}

function removeExercise(exercise: FitnessExercise) {
  uni.showModal({
    title: `移除“${exercise.name}”`,
    content: '历史训练记录会保留，只从今后的计划中移除。',
    confirmText: '移除',
    success: async (result) => {
      if (!result.confirm || saving.value)
        return
      saving.value = true
      try {
        await fitnessApi.archiveExercise(exercise.id)
        await load()
      }
      catch {
        error.value = '动作没有移除成功，请稍后重试。'
      }
      finally {
        saving.value = false
      }
    },
  })
}
</script>

<template>
  <view class="fitness-page pt-safe">
    <view class="fitness-shell">
      <view class="fitness-heading preview-heading">
        <text class="fitness-eyebrow">CHOOSE YOUR FOCUS</text>
        <view class="fitness-row-between preview-title-row">
          <view>
            <text class="fitness-title">{{ plan?.name || '训练部位' }}</text>
            <text class="fitness-subtitle">自由选择动作，准备好后再开始今天的训练。</text>
          </view>
          <text class="preview-count">{{ exercises.length }}<text class="preview-count-unit">动作</text></text>
        </view>
      </view>

      <text v-if="error" class="fitness-error">{{ error }}</text>

      <view class="fitness-section preview-actions-section">
        <view class="fitness-row-between section-heading-row">
          <view>
            <text class="fitness-section-title">今天练这些</text>
            <text class="fitness-meta">选择动作后立即开始记录，每组独立保存</text>
          </view>
        </view>
        <view v-if="loading" class="fitness-empty">
          正在读取动作…
        </view>
        <view v-else-if="!exercises.length" class="fitness-empty">
          还没有动作，先添加一个再开始。
        </view>
        <view v-for="(exercise, index) in exercises" :key="exercise.id" class="preview-exercise-row">
          <view class="preview-exercise-index">
            {{ String(index + 1).padStart(2, '0') }}
          </view>
          <view class="fitness-list-copy" @click="startExercise(exercise)">
            <text class="fitness-list-title">{{ exercise.name }}</text>
            <text class="fitness-meta">建议 {{ exercise.defaultWeight }} kg · {{ exercise.defaultReps }} 次</text>
          </view>
          <button class="preview-remove" aria-label="停用动作" @click.stop="removeExercise(exercise)">
            停用
          </button>
        </view>
      </view>

      <view class="fitness-section add-exercise-section">
        <text class="fitness-section-title">增加动作</text>
        <text class="preview-field-label">动作名称</text>
        <input v-model="newExerciseName" class="fitness-input" placeholder="例如：上斜哑铃卧推">
        <view class="preview-input-row">
          <view class="preview-input-field">
            <text class="preview-field-label">默认重量（kg）</text>
            <input v-model.number="newExerciseWeight" class="fitness-input" type="digit">
          </view>
          <view class="preview-input-field">
            <text class="preview-field-label">默认次数（次）</text>
            <input v-model.number="newExerciseReps" class="fitness-input" type="number">
          </view>
          <button class="fitness-secondary preview-add-button" :disabled="saving" @click="addExercise">
            添加
          </button>
        </view>
      </view>
      <text class="preview-safe-note">停用只影响今后的计划，历史训练记录不会删除。</text>

      <view class="preview-start-bar">
        <button class="fitness-primary" :disabled="saving || loading || !plan" @click="startWorkout">
          {{ saving ? '处理中…' : `开始${plan?.name || ''}训练` }}
        </button>
      </view>
    </view>
  </view>
</template>

<style scoped lang="scss">
@import '@/modules/fitness/fitness.scss';

.preview-heading {
  padding-bottom: 28rpx;
}

.preview-title-row {
  align-items: flex-end;
  gap: 16rpx;
}

.preview-title-row .fitness-title {
  margin-top: 12rpx;
}

.preview-count {
  flex: none;
  color: #176b57;
  font-family: Georgia, serif;
  font-size: 58rpx;
  font-weight: 700;
  line-height: 1;
}

.preview-count-unit {
  margin-left: 6rpx;
  color: #777a73;
  font-family: 'PingFang SC', sans-serif;
  font-size: 18rpx;
  font-weight: 400;
}

.preview-actions-section {
  padding-top: 32rpx;
}

.preview-exercise-row {
  display: flex;
  min-height: 116rpx;
  align-items: center;
  gap: 18rpx;
  border-top: 1rpx solid #d5d3cc;
}

.preview-exercise-row:last-child {
  border-bottom: 1rpx solid #d5d3cc;
}

.preview-exercise-index {
  width: 46rpx;
  color: #cf533d;
  font-family: Georgia, serif;
  font-size: 22rpx;
}

.preview-remove {
  min-width: 74rpx;
  height: 58rpx;
  padding: 0 12rpx;
  border: 1rpx solid #d5b2a9;
  border-radius: 2rpx;
  color: #a43f2e;
  background: transparent;
  font-size: 19rpx;
  line-height: 54rpx;
}

.add-exercise-section {
  padding-bottom: 26rpx;
}

.preview-input-row {
  display: grid;
  grid-template-columns: 1fr 1fr auto;
  align-items: end;
  gap: 12rpx;
  margin-top: 16rpx;
}

.preview-field-label {
  display: block;
  margin: 0 0 8rpx;
  color: #626760;
  font-size: 19rpx;
  font-weight: 700;
}

.preview-safe-note {
  display: block;
  margin-top: 16rpx;
  color: #777a73;
  font-size: 18rpx;
  line-height: 1.5;
}

.preview-input-field .fitness-meta {
  margin-bottom: 7rpx;
}

.preview-add-button {
  min-width: 112rpx;
  padding: 0 18rpx;
}

.preview-start-bar {
  padding-top: 22rpx;
}
</style>
