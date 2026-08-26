<script lang="ts" setup>
import type { ExerciseLog, WorkoutSet } from '@/modules/fitness'
import NumberStepper from '@/modules/fitness/components/NumberStepper.vue'
import {
  clearFitnessDraft,
  createRequestId,
  fitnessApi,
  loadFitnessDraft,
  saveFitnessDraft,
  useFitnessStore,
} from '@/modules/fitness'

definePage({ style: { navigationBarTitleText: '动作记录' } })

const store = useFitnessStore()
const sessionId = ref('')
const exerciseId = ref('')
const log = ref<ExerciseLog | null>(null)
const weight = ref(0)
const reps = ref(8)
const saving = ref(false)
const error = ref('')
const savedNotice = ref('')
let pendingRequestId = ''

onLoad((query) => {
  sessionId.value = String(query?.sessionId || '')
  exerciseId.value = String(query?.exerciseId || '')
  load()
})

watch([weight, reps], () => {
  if (exerciseId.value)
    saveFitnessDraft(exerciseId.value, { weight: weight.value, reps: reps.value })
})

async function load() {
  try {
    const value = await fitnessApi.getExerciseLog(sessionId.value, exerciseId.value)
    log.value = value
    const draft = loadFitnessDraft(exerciseId.value)
    weight.value = draft?.weight ?? value.suggestedWeight
    reps.value = draft?.reps ?? value.suggestedReps
  }
  catch {
    error.value = '无法读取动作记录。'
  }
}

async function completeSet() {
  if (!log.value || saving.value)
    return
  saving.value = true
  error.value = ''
  pendingRequestId ||= createRequestId()
  saveFitnessDraft(exerciseId.value, { weight: weight.value, reps: reps.value })
  try {
    await store.recordSet(log.value, weight.value, reps.value, pendingRequestId)
    pendingRequestId = ''
    clearFitnessDraft(exerciseId.value)
    savedNotice.value = '已保存到本地数据库'
    setTimeout(() => {
      savedNotice.value = ''
    }, 2200)
  }
  catch {
    error.value = '这一组尚未保存，输入已保留，可以直接重试。'
  }
  finally {
    saving.value = false
  }
}

function deleteSet(set: WorkoutSet) {
  uni.showModal({
    title: `删除第 ${set.setOrder} 组`,
    content: `${set.weight} kg × ${set.reps}`,
    success: async (result) => {
      if (!result.confirm || !log.value)
        return
      await fitnessApi.deleteSet(set.id)
      log.value.currentSets = log.value.currentSets.filter(item => item.id !== set.id)
    },
  })
}
</script>

<template>
  <view class="fitness-page pt-safe">
    <view class="fitness-shell">
      <view class="fitness-heading">
        <text class="fitness-eyebrow">SET LOGGING</text>
        <text class="fitness-title">{{ log?.exercise.name || '动作' }}</text>
        <view class="fitness-row-between exercise-heading-meta">
          <text class="fitness-subtitle">每组完成后立即保存到本地数据库，随时可以调整。</text>
          <text class="exercise-set-count">{{ log?.currentSets.length || 0 }} 组</text>
        </view>
      </view>

      <view class="fitness-section">
        <view class="fitness-row-between section-heading-row">
          <view>
            <text class="fitness-section-title">今天已完成</text>
            <text class="fitness-meta">已保存的组可以删除后重新记录</text>
          </view>
          <text class="exercise-total-sets">{{ log?.currentSets.length || 0 }} 组</text>
        </view>
        <view v-if="log?.currentSets.length" class="completed-set-list">
          <view v-for="set in log.currentSets" :key="set.id" class="set-line completed-set-line">
            <text class="set-order">{{ String(set.setOrder).padStart(2, '0') }}</text>
            <text class="set-value">{{ set.weight }} kg × {{ set.reps }} 次</text>
            <button class="set-delete" aria-label="删除这一组" @click="deleteSet(set)">
              ×
            </button>
          </view>
        </view>
        <text v-else class="fitness-empty compact-empty">完成第一组后会立即显示在这里。</text>
      </view>

      <view class="fitness-section current-section">
        <view class="fitness-row-between section-heading-row">
          <view>
            <text class="fitness-section-title">当前调整</text>
            <text class="fitness-meta">设置下一组的重量和次数</text>
          </view>
          <text class="current-marker">NEXT</text>
        </view>
        <view class="current-input-panel">
          <NumberStepper v-model="weight" label="重量" unit="kg" :step="2.5" />
          <NumberStepper v-model="reps" label="次数" unit="次" :step="1" />
        </view>
        <text v-if="error" class="fitness-error">{{ error }}</text>
        <text v-if="savedNotice" class="saved-notice">{{ savedNotice }}</text>
        <button class="fitness-primary" :disabled="saving || !log" @click="completeSet">
          {{ saving ? '正在保存…' : '完成一组' }}
        </button>
      </view>

      <view class="fitness-section previous-section">
        <text class="fitness-section-title">上一次训练</text>
        <view v-if="log?.previousSets.length">
          <view v-for="set in log.previousSets" :key="set.id" class="set-line">
            <text class="set-order">{{ String(set.setOrder).padStart(2, '0') }}</text>
            <text>{{ set.weight }} kg × {{ set.reps }}</text>
          </view>
        </view>
        <text v-else class="fitness-empty">还没有这个动作的历史记录。</text>
      </view>
    </view>
  </view>
</template>

<style scoped lang="scss">
@import '@/modules/fitness/fitness.scss';

.exercise-heading-meta {
  align-items: flex-end;
  gap: 16rpx;
}

.exercise-heading-meta .fitness-subtitle {
  flex: 1;
}

.exercise-set-count,
.exercise-total-sets {
  flex: none;
  color: #176b57;
  font-family: Georgia, serif;
  font-size: 23rpx;
  font-weight: 700;
}

.section-heading-row {
  align-items: flex-end;
  margin-bottom: 18rpx;
}

.section-heading-row .fitness-section-title {
  margin-bottom: 4rpx;
}

.completed-set-list {
  border-top: 1rpx solid #d5d3cc;
}

.completed-set-line {
  min-height: 82rpx;
  border-top: 0;
  border-bottom: 1rpx solid #d5d3cc;
}

.compact-empty {
  padding: 14rpx 0 4rpx;
}

.current-section {
  padding-top: 34rpx;
  padding-bottom: 34rpx;
  border-bottom: 2rpx solid #1d2420;
}

.current-marker {
  padding: 7rpx 10rpx;
  color: #fff;
  background: #cf533d;
  font-size: 17rpx;
  font-weight: 700;
  letter-spacing: 0;
}

.current-input-panel {
  padding: 4rpx 20rpx 14rpx;
  border: 1rpx solid #c8c8c0;
  background: #ebece6;
}

.current-input-panel :deep(.stepper) {
  padding: 18rpx 0;
}

.current-input-panel :deep(.stepper-control) {
  min-height: 112rpx;
}

.current-input-panel :deep(.stepper-number) {
  font-size: 58rpx;
}

.current-input-panel :deep(.stepper-button) {
  width: 104rpx;
  border-color: #777a73;
  background: #fcfbf7;
}

.saved-notice {
  display: block;
  margin: 12rpx 0 4rpx;
  color: #176b57;
  font-size: 20rpx;
  font-weight: 700;
  text-align: center;
}

.previous-section {
  padding-top: 30rpx;
}

.set-line {
  display: grid;
  grid-template-columns: 50rpx minmax(0, 1fr) 64rpx;
  min-height: 72rpx;
  align-items: center;
  border-top: 1rpx solid #d5d3cc;
  font-size: 25rpx;
}

.set-line:last-child {
  border-bottom: 1rpx solid #d5d3cc;
}

.set-order {
  color: #777a73;
  font-family: Georgia, serif;
}

.set-value {
  font-weight: 650;
}

.set-delete {
  width: 56rpx;
  height: 56rpx;
  padding: 0;
  border: 0;
  color: #a43f2e;
  background: transparent;
  font-size: 32rpx;
}
</style>
