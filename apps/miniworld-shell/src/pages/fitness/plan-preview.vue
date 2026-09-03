<script lang="ts" setup>
import type { FitnessExercise, FitnessPlan } from '@/modules/fitness'
import { fitnessApi, useFitnessStore, useFitnessWorkoutStatus } from '@/modules/fitness'
import ExerciseDefaultsFields from '@/modules/fitness/components/ExerciseDefaultsFields.vue'
import FitnessExerciseRow from '@/modules/fitness/components/FitnessExerciseRow.vue'
import FitnessPageShell from '@/modules/fitness/components/FitnessPageShell.vue'
import FitnessSectionHeader from '@/modules/fitness/components/FitnessSectionHeader.vue'

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
const addingExercise = ref(false)
const { workoutStatus, workoutActionLabel, handleWorkoutAction } = useFitnessWorkoutStatus('other')

const hasActiveWorkout = computed(() => workoutStatus.value?.state === 'ACTIVE_TODAY' || workoutStatus.value?.state === 'UNFINISHED_PREVIOUS_DAY')
const canStartWorkout = computed(() => Boolean(plan.value && exercises.value.length && !hasActiveWorkout.value))

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
  if (!plan.value || !exercises.value.length || hasActiveWorkout.value || saving.value)
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
  const active = store.state.activeSession
  if (active) {
    if (active.planId === plan.value.id && active.exercises.some(item => item.exercise.id === exercise.id)) {
      uni.redirectTo({ url: `/pages/fitness/exercise?sessionId=${active.id}&exerciseId=${exercise.id}` })
      return
    }
    error.value = `“${active.planNameSnapshot}”训练仍在进行，请先继续或结束。`
    return
  }
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
    addingExercise.value = false
    await load()
  }
  catch {
    error.value = '动作没有添加成功，请稍后重试。'
  }
  finally {
    saving.value = false
  }
}

function continueActiveWorkout() {
  if (workoutStatus.value)
    handleWorkoutAction(workoutStatus.value.state)
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
  <FitnessPageShell
    eyebrow="训练计划"
    :title="plan?.name || '训练部位'"
    subtitle="确认动作与建议重量，准备好后开始记录。"
    :error="error"
    :workout-status="workoutStatus"
    :workout-action-label="workoutActionLabel"
    compact-heading
    @workout-action="handleWorkoutAction"
  >
    <template #heading>
      <view class="fitness-row-between preview-title-row">
        <view>
          <text class="fitness-title">{{ plan?.name || '训练部位' }}</text>
          <text class="fitness-subtitle">确认动作与建议重量，准备好后开始记录。</text>
        </view>
        <text class="preview-count">{{ exercises.length }}<text class="preview-count-unit">动作</text></text>
      </view>
    </template>

    <view class="fitness-section preview-actions-section">
      <FitnessSectionHeader title="训练动作" subtitle="进入动作会开始或继续本次训练">
        <template #right>
          <wd-button
            v-if="!hasActiveWorkout"
            type="primary"
            variant="text"
            size="medium"
            @click="addingExercise = !addingExercise"
          >
            {{ addingExercise ? '收起' : '添加动作' }}
          </wd-button>
        </template>
      </FitnessSectionHeader>
      <view v-if="loading" class="fitness-loading-state">
        <wd-loading size="22px" />
        <text class="fitness-meta">正在读取动作</text>
      </view>
      <view v-else-if="!exercises.length" class="fitness-empty-state">
        <wd-empty tip="还没有训练动作" icon-size="64" />
        <text class="fitness-note">添加第一个动作后才能开始训练。</text>
      </view>
      <FitnessExerciseRow
        v-for="(exercise, index) in exercises"
        :key="exercise.id"
        :exercise="exercise"
        :index="index"
        :meta="`建议 ${exercise.defaultWeight} kg × ${exercise.defaultReps} 次`"
        :action-label="hasActiveWorkout ? '' : '停用'"
        :disabled="saving"
        @select="startExercise(exercise)"
        @action="removeExercise(exercise)"
      />
    </view>

    <view v-if="addingExercise && !hasActiveWorkout" class="fitness-section add-exercise-section">
      <FitnessSectionHeader title="添加动作" subtitle="默认值会作为第一组建议，可在训练时调整" />
      <ExerciseDefaultsFields v-model:name="newExerciseName" v-model:weight="newExerciseWeight" v-model:reps="newExerciseReps">
        <template #action>
          <wd-button class="fitness-primary" type="primary" size="large" block :loading="saving" :disabled="saving || !newExerciseName.trim()" @click="addExercise">
            保存动作
          </wd-button>
        </template>
      </ExerciseDefaultsFields>
    </view>

    <view class="fitness-primary-bar">
      <wd-button
        v-if="hasActiveWorkout"
        class="fitness-primary"
        type="primary"
        size="large"
        block
        @click="continueActiveWorkout"
      >
        继续当前训练
      </wd-button>
      <wd-button
        v-else-if="!loading && !exercises.length"
        class="fitness-primary"
        type="primary"
        size="large"
        block
        @click="addingExercise = true"
      >
        添加第一个动作
      </wd-button>
      <wd-button
        v-else
        class="fitness-primary"
        type="primary"
        size="large"
        block
        :loading="saving"
        :disabled="!canStartWorkout || loading"
        @click="startWorkout"
      >
        开始{{ plan?.name || '' }}训练
      </wd-button>
    </view>
  </FitnessPageShell>
</template>

<style scoped lang="scss">
.preview-title-row {
  align-items: flex-end;
  gap: var(--mw-space-4);
}

.preview-title-row .fitness-title {
  margin-top: var(--mw-space-2);
}

.preview-count {
  flex: none;
  color: var(--mw-color-primary);
  font-size: var(--mw-font-data);
  font-weight: 700;
  line-height: 1;
}

.preview-count-unit {
  margin-left: var(--mw-space-1);
  color: var(--mw-color-text-secondary);
  font-size: var(--mw-font-auxiliary);
  font-weight: 400;
}

.preview-actions-section {
  padding-top: var(--mw-space-5);
}
</style>
