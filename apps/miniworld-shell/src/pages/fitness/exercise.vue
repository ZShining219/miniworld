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
        <text class="fitness-subtitle">调整重量和次数，然后立即保存这一组。</text>
      </view>

      <view class="fitness-section">
        <text class="fitness-section-title">上一次训练</text>
        <view v-if="log?.previousSets.length">
          <view v-for="set in log.previousSets" :key="set.id" class="set-line">
            <text>{{ set.setOrder }}</text>
            <text>{{ set.weight }} kg × {{ set.reps }}</text>
          </view>
        </view>
        <text v-else class="fitness-empty">还没有这个动作的历史记录。</text>
      </view>

      <view class="fitness-section">
        <text class="fitness-section-title">当前</text>
        <NumberStepper v-model="weight" label="重量" unit="kg" :step="2.5" />
        <NumberStepper v-model="reps" label="次数" :step="1" />
        <text v-if="error" class="fitness-error">{{ error }}</text>
        <button class="fitness-primary" :disabled="saving || !log" @click="completeSet">
          {{ saving ? '正在保存…' : '完成一组' }}
        </button>
      </view>

      <view class="fitness-section">
        <text class="fitness-section-title">今天已完成</text>
        <view v-if="log?.currentSets.length">
          <view v-for="set in log.currentSets" :key="set.id" class="set-line">
            <text class="set-order">{{ set.setOrder }}</text>
            <text class="set-value">{{ set.weight }} kg × {{ set.reps }}</text>
            <button class="set-delete" aria-label="删除这一组" @click="deleteSet(set)">
              ×
            </button>
          </view>
        </view>
        <text v-else class="fitness-empty">完成第一组后会立即显示在这里。</text>
      </view>
    </view>
  </view>
</template>

<style scoped lang="scss">
@import '@/modules/fitness/fitness.scss';

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
