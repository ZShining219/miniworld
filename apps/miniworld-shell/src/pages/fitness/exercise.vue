<script lang="ts" setup>
import type { ExerciseLog } from '@/modules/fitness'
import FitnessPageShell from '@/modules/fitness/components/FitnessPageShell.vue'
import FitnessSectionHeader from '@/modules/fitness/components/FitnessSectionHeader.vue'
import NumberStepper from '@/modules/fitness/components/NumberStepper.vue'
import WorkoutSetList from '@/modules/fitness/components/WorkoutSetList.vue'
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
</script>

<template>
  <FitnessPageShell
    eyebrow="SET LOGGING"
    :title="log?.exercise.name || '动作'"
    subtitle="每组完成后立即保存到本地数据库，随时可以调整。"
  >
    <template #heading>
      <text class="fitness-title">{{ log?.exercise.name || '动作' }}</text>
      <view class="fitness-row-between exercise-heading-meta">
        <text class="fitness-subtitle">每组完成后立即保存到本地数据库，随时可以调整。</text>
        <text class="exercise-set-count">{{ log?.currentSets.length || 0 }} 组</text>
      </view>
    </template>

    <view class="fitness-section">
      <FitnessSectionHeader title="今天已完成" subtitle="已保存的组只读保留，避免误操作清理训练数据">
        <template #right>
          <text class="exercise-total-sets">{{ log?.currentSets.length || 0 }} 组</text>
        </template>
      </FitnessSectionHeader>
      <WorkoutSetList v-if="log?.currentSets.length" :sets="log.currentSets" show-reps-unit emphasized />
      <text v-else class="fitness-empty compact-empty">完成第一组后会立即显示在这里；已保存记录只读保留。</text>
    </view>

    <view class="fitness-section current-section">
      <FitnessSectionHeader title="当前调整" subtitle="设置下一组的重量和次数">
        <template #right>
          <text class="current-marker">NEXT</text>
        </template>
      </FitnessSectionHeader>
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
      <WorkoutSetList v-if="log?.previousSets.length" :sets="log.previousSets" />
      <text v-else class="fitness-empty">还没有这个动作的历史记录。</text>
    </view>
  </FitnessPageShell>
</template>

<style scoped lang="scss">
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
</style>
