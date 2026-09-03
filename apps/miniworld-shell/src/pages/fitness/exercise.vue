<script lang="ts" setup>
import type { ExerciseLog, SessionDetail } from '@/modules/fitness'
import FitnessPageShell from '@/modules/fitness/components/FitnessPageShell.vue'
import FitnessExerciseSwitcher from '@/modules/fitness/components/FitnessExerciseSwitcher.vue'
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
  useFitnessWorkoutStatus,
} from '@/modules/fitness'

definePage({ style: { navigationBarTitleText: '动作记录' } })

const store = useFitnessStore()
const sessionId = ref('')
const exerciseId = ref('')
const log = ref<ExerciseLog | null>(null)
const session = ref<SessionDetail | null>(null)
const weight = ref(0)
const reps = ref(8)
const weightStep = ref(2.5)
let confirmedWeightStep = 2.5
const saving = ref(false)
const savingWeightStep = ref(false)
const error = ref('')
const savedNotice = ref('')
let pendingRequestId = ''
const { workoutStatus, workoutActionLabel, handleWorkoutAction } = useFitnessWorkoutStatus('exercise')

onLoad((query) => {
  sessionId.value = String(query?.sessionId || '')
  exerciseId.value = String(query?.exerciseId || '')
  load()
})

watch([weight, reps], () => {
  if (exerciseId.value)
    saveDraft()
})

function saveDraft() {
  saveFitnessDraft(exerciseId.value, {
    weight: weight.value,
    reps: reps.value,
    clientRequestId: pendingRequestId || undefined,
  })
}

async function load() {
  try {
    const [value, sessionValue] = await Promise.all([
      fitnessApi.getExerciseLog(sessionId.value, exerciseId.value),
      store.loadSession(sessionId.value),
    ])
    log.value = value
    session.value = sessionValue
    const draft = loadFitnessDraft(exerciseId.value)
    weight.value = draft?.weight ?? value.suggestedWeight
    reps.value = draft?.reps ?? value.suggestedReps
    pendingRequestId = draft?.clientRequestId || ''
    weightStep.value = value.exercise.weightStep
    confirmedWeightStep = value.exercise.weightStep
  }
  catch {
    error.value = '无法读取动作记录。'
  }
}

function switchExercise(nextExerciseId: string) {
  if (saving.value || savingWeightStep.value || nextExerciseId === exerciseId.value)
    return
  saveDraft()
  uni.redirectTo({ url: `/pages/fitness/exercise?sessionId=${sessionId.value}&exerciseId=${nextExerciseId}` })
}

async function saveWeightStep(nextStep: number) {
  if (!log.value || savingWeightStep.value || nextStep === weightStep.value)
    return
  const previous = confirmedWeightStep
  weightStep.value = nextStep
  savingWeightStep.value = true
  error.value = ''
  try {
    const updated = await fitnessApi.updateExercise(log.value.exercise.id, { weightStep: nextStep })
    log.value.exercise.weightStep = updated.weightStep
    const summary = session.value?.exercises.find(item => item.exercise.id === updated.id)
    if (summary)
      summary.exercise.weightStep = updated.weightStep
    confirmedWeightStep = updated.weightStep
    weightStep.value = updated.weightStep
  }
  catch {
    weightStep.value = previous
    error.value = `档位保存失败，已恢复为 ${previous} kg。`
  }
  finally {
    savingWeightStep.value = false
  }
}

async function completeSet() {
  if (!log.value || saving.value)
    return
  saving.value = true
  error.value = ''
  pendingRequestId ||= createRequestId()
  saveDraft()
  try {
    await store.recordSet(log.value, weight.value, reps.value, pendingRequestId)
    const summary = session.value?.exercises.find(item => item.exercise.id === exerciseId.value)
    if (summary)
      summary.completedSetCount = log.value.currentSets.length
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
    eyebrow="动作记录"
    :title="log?.exercise.name || '动作'"
    subtitle="调整下一组数据，完成后立即保存。"
    :error="error"
    :workout-status="workoutStatus"
    :workout-action-label="workoutActionLabel"
    @workout-action="handleWorkoutAction"
  >
    <template #heading>
      <text class="fitness-title">{{ log?.exercise.name || '动作' }}</text>
      <view class="fitness-row-between exercise-heading-meta">
        <text class="fitness-subtitle">调整下一组数据，完成后立即保存。</text>
        <text class="exercise-set-count">已完成 {{ log?.currentSets.length || 0 }} 组</text>
      </view>
    </template>

    <FitnessExerciseSwitcher
      v-if="session?.exercises.length"
      :exercises="session.exercises"
      :current-id="exerciseId"
      :disabled="saving || savingWeightStep"
      @select="switchExercise"
    />

    <view class="fitness-section current-section">
      <FitnessSectionHeader title="下一组" subtitle="重量可直接输入，也可用两侧按钮调整">
        <template #right>
          <text class="current-marker">待完成</text>
        </template>
      </FitnessSectionHeader>
      <view class="current-input-panel">
        <NumberStepper
          v-model="weight"
          label="重量"
          unit="kg"
          :step="weightStep"
          :step-options="[1, 2, 2.5, 5]"
          :step-options-disabled="savingWeightStep"
          :min="0"
          :max="9999"
          editable
          @update:step="saveWeightStep"
        />
        <NumberStepper v-model="reps" label="次数" unit="次" :step="1" :min="0" :max="999" />
      </view>
      <text v-if="savedNotice" class="saved-notice" role="status">✓ {{ savedNotice }}</text>
      <view class="fitness-primary-bar set-action-bar">
        <wd-button class="fitness-primary" type="primary" size="large" block :loading="saving" :disabled="saving || !log" @click="completeSet">
          完成并保存这一组
        </wd-button>
      </view>
    </view>

    <view class="fitness-section">
      <FitnessSectionHeader title="今天已完成" subtitle="已保存到本地数据库，只读保留">
        <template #right>
          <text class="exercise-total-sets">{{ log?.currentSets.length || 0 }} 组</text>
        </template>
      </FitnessSectionHeader>
      <WorkoutSetList v-if="log?.currentSets.length" :sets="log.currentSets" show-reps-unit emphasized />
      <view v-else class="fitness-empty-state compact-empty">
        <wd-empty tip="还没有完成的组" icon-size="56" />
        <text class="fitness-note">完成第一组后会立即显示在这里。</text>
      </view>
    </view>

    <view class="fitness-section previous-section">
      <text class="fitness-section-title">上一次训练</text>
      <WorkoutSetList v-if="log?.previousSets.length" :sets="log.previousSets" />
      <view v-else class="fitness-empty-state compact-empty">
        <wd-empty tip="暂无历史记录" icon-size="56" />
      </view>
    </view>
  </FitnessPageShell>
</template>

<style scoped lang="scss">
.exercise-heading-meta {
  align-items: flex-end;
  gap: var(--mw-space-4);
}

.exercise-heading-meta .fitness-subtitle {
  flex: 1;
}

.exercise-set-count,
.exercise-total-sets {
  flex: none;
  color: var(--mw-color-primary);
  font-size: var(--mw-font-body);
  font-weight: 700;
}

.compact-empty {
  padding: var(--mw-space-3) 0 var(--mw-space-1);
}

.current-section {
  padding-top: var(--mw-space-5);
}

.current-marker {
  padding: var(--mw-space-1) var(--mw-space-2);
  border-radius: var(--mw-radius-pill);
  color: var(--mw-color-primary-strong);
  background: var(--mw-color-primary-soft);
  font-size: var(--mw-font-auxiliary);
  font-weight: 700;
  letter-spacing: 0;
}

.current-input-panel {
  padding: var(--mw-space-2) var(--mw-space-3) var(--mw-space-3);
  border: 1px solid var(--mw-color-border);
  border-radius: var(--mw-radius-md);
  background: var(--mw-color-surface-muted);
}

.current-input-panel :deep(.stepper) {
  padding: var(--mw-space-3) 0;
}

.saved-notice {
  display: block;
  margin: var(--mw-space-3) 0 var(--mw-space-1);
  color: var(--mw-color-success);
  font-size: var(--mw-font-body);
  font-weight: 700;
  text-align: center;
}

.previous-section {
  padding-top: var(--mw-space-5);
}

.set-action-bar {
  margin-top: var(--mw-space-2);
  margin-right: 0;
  margin-left: 0;
  padding-right: 0;
  padding-left: 0;
}
</style>
