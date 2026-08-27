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
const { workoutStatus, workoutActionLabel, handleWorkoutAction } = useFitnessWorkoutStatus('other')

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
  <FitnessPageShell
    eyebrow="CHOOSE YOUR FOCUS"
    :title="plan?.name || '训练部位'"
    subtitle="自由选择动作，准备好后再开始今天的训练。"
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
          <text class="fitness-subtitle">自由选择动作，准备好后再开始今天的训练。</text>
        </view>
        <text class="preview-count">{{ exercises.length }}<text class="preview-count-unit">动作</text></text>
      </view>
    </template>

    <view class="fitness-section preview-actions-section">
      <FitnessSectionHeader title="今天练这些" subtitle="选择动作后立即开始记录，每组独立保存" />
      <view v-if="loading" class="fitness-empty">
        正在读取动作…
      </view>
      <view v-else-if="!exercises.length" class="fitness-empty">
        还没有动作，先添加一个再开始。
      </view>
      <FitnessExerciseRow
        v-for="(exercise, index) in exercises"
        :key="exercise.id"
        :exercise="exercise"
        :index="index"
        :meta="`建议 ${exercise.defaultWeight} kg · ${exercise.defaultReps} 次`"
        action-label="停用"
        :disabled="saving"
        @select="startExercise(exercise)"
        @action="removeExercise(exercise)"
      />
    </view>

    <view class="fitness-section add-exercise-section">
      <text class="fitness-section-title">增加动作</text>
      <ExerciseDefaultsFields v-model:name="newExerciseName" v-model:weight="newExerciseWeight" v-model:reps="newExerciseReps">
        <template #action>
          <button class="fitness-secondary preview-add-button" :disabled="saving" @click="addExercise">
            添加
          </button>
        </template>
      </ExerciseDefaultsFields>
    </view>
    <text class="preview-safe-note">停用只影响今后的计划，历史训练记录不会删除。</text>

    <view class="preview-start-bar">
      <button class="fitness-primary" :disabled="saving || loading || !plan" @click="startWorkout">
        {{ saving ? '处理中…' : `开始${plan?.name || ''}训练` }}
      </button>
    </view>
  </FitnessPageShell>
</template>

<style scoped lang="scss">
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

.add-exercise-section {
  padding-bottom: 26rpx;
}

.preview-safe-note {
  display: block;
  margin-top: 16rpx;
  color: #777a73;
  font-size: 18rpx;
  line-height: 1.5;
}

.preview-add-button {
  min-width: 112rpx;
  padding: 0 18rpx;
}

.preview-start-bar {
  padding-top: 22rpx;
}
</style>
