<script lang="ts" setup>
import type { FitnessExercise, FitnessPlan } from '@/modules/fitness'
import { fitnessApi, useFitnessWorkoutStatus } from '@/modules/fitness'
import ExerciseDefaultsFields from '@/modules/fitness/components/ExerciseDefaultsFields.vue'
import FitnessExerciseEditorRow from '@/modules/fitness/components/FitnessExerciseEditorRow.vue'
import FitnessPageShell from '@/modules/fitness/components/FitnessPageShell.vue'
import FitnessPlanEditorRow from '@/modules/fitness/components/FitnessPlanEditorRow.vue'

definePage({ style: { navigationBarTitleText: '计划管理' } })

const plans = ref<FitnessPlan[]>([])
const exercises = ref<FitnessExercise[]>([])
const selectedPlanId = ref('')
const newPlanName = ref('')
const newExerciseName = ref('')
const newExerciseWeight = ref(0)
const newExerciseReps = ref(8)
const error = ref('')
const { workoutStatus, workoutActionLabel, handleWorkoutAction } = useFitnessWorkoutStatus('other')

onLoad(() => loadPlans())

async function loadPlans(preferredId?: string) {
  plans.value = await fitnessApi.listPlans()
  const id = preferredId || selectedPlanId.value || plans.value[0]?.id
  if (id)
    await selectPlan(id)
}

async function selectPlan(planId: string) {
  selectedPlanId.value = planId
  exercises.value = await fitnessApi.listExercises(planId)
}

async function addPlan() {
  const name = newPlanName.value.trim()
  if (!name)
    return
  const plan = await fitnessApi.createPlan({ name })
  newPlanName.value = ''
  await loadPlans(plan.id)
}

async function savePlan(plan: FitnessPlan) {
  await fitnessApi.updatePlan(plan.id, { name: plan.name })
  await loadPlans(plan.id)
}

function archivePlan(plan: FitnessPlan) {
  uni.showModal({
    title: `归档“${plan.name}”`,
    content: '过去的训练历史不会被删除。',
    success: async (result) => {
      if (!result.confirm)
        return
      try {
        await fitnessApi.archivePlan(plan.id)
        selectedPlanId.value = ''
        await loadPlans()
      }
      catch {
        error.value = '进行中的训练计划不能归档。'
      }
    },
  })
}

async function addExercise() {
  const name = newExerciseName.value.trim()
  if (!name || !selectedPlanId.value)
    return
  await fitnessApi.createExercise({
    planId: selectedPlanId.value,
    name,
    defaultWeight: newExerciseWeight.value,
    defaultReps: newExerciseReps.value,
  })
  newExerciseName.value = ''
  await selectPlan(selectedPlanId.value)
}

async function saveExercise(exercise: FitnessExercise) {
  await fitnessApi.updateExercise(exercise.id, {
    name: exercise.name,
    defaultWeight: exercise.defaultWeight,
    defaultReps: exercise.defaultReps,
  })
  await selectPlan(selectedPlanId.value)
}

function archiveExercise(exercise: FitnessExercise) {
  uni.showModal({
    title: `归档“${exercise.name}”`,
    content: '过去的组记录会继续保留。',
    success: async (result) => {
      if (!result.confirm)
        return
      await fitnessApi.archiveExercise(exercise.id)
      await selectPlan(selectedPlanId.value)
    },
  })
}

async function moveExercise(index: number, direction: number) {
  const target = index + direction
  if (target < 0 || target >= exercises.value.length)
    return
  const reordered = [...exercises.value]
  ;[reordered[index], reordered[target]] = [reordered[target], reordered[index]]
  exercises.value = await fitnessApi.reorderExercises(selectedPlanId.value, reordered.map(item => item.id))
}
</script>

<template>
  <FitnessPageShell
    eyebrow="FITNESS SETTINGS"
    title="计划与动作"
    subtitle="归档只影响今后的计划，过去的训练不会被删除。"
    :error="error"
    :workout-status="workoutStatus"
    :workout-action-label="workoutActionLabel"
    @workout-action="handleWorkoutAction"
  >
    <view class="fitness-section">
      <text class="fitness-section-title">训练计划</text>
      <FitnessPlanEditorRow
        v-for="plan in plans"
        :key="plan.id"
        :plan="plan"
        :selected="selectedPlanId === plan.id"
        @select="selectPlan(plan.id)"
        @update:name="plan.name = $event"
        @save="savePlan(plan)"
        @archive="archivePlan(plan)"
      />
      <view class="add-row">
        <text class="new-item-label">新计划名称</text>
        <input v-model="newPlanName" class="fitness-input" placeholder="新计划名称">
        <button class="fitness-secondary" @click="addPlan">
          新增计划
        </button>
      </view>
    </view>

    <view v-if="selectedPlanId" class="fitness-section">
      <text class="fitness-section-title">计划动作</text>
      <FitnessExerciseEditorRow
        v-for="(exercise, index) in exercises"
        :key="exercise.id"
        :exercise="exercise"
        :first="index === 0"
        :last="index === exercises.length - 1"
        @update:name="exercise.name = $event"
        @update:weight="exercise.defaultWeight = $event"
        @update:reps="exercise.defaultReps = $event"
        @move="moveExercise(index, $event)"
        @save="saveExercise(exercise)"
        @archive="archiveExercise(exercise)"
      />
      <view class="new-exercise">
        <ExerciseDefaultsFields v-model:name="newExerciseName" v-model:weight="newExerciseWeight" v-model:reps="newExerciseReps">
          <template #action>
            <button class="fitness-secondary" @click="addExercise">
              新增动作
            </button>
          </template>
        </ExerciseDefaultsFields>
      </view>
    </view>
  </FitnessPageShell>
</template>

<style scoped lang="scss">
.new-item-label {
  display: block;
  color: #777a73;
  font-size: 19rpx;
  font-weight: 700;
}

.add-row,
.new-exercise {
  display: grid;
  gap: 14rpx;
  padding-top: 26rpx;
}
</style>
