<script lang="ts" setup>
import type { FitnessExercise, FitnessPlan } from '@/modules/fitness'
import { fitnessApi } from '@/modules/fitness'

definePage({ style: { navigationBarTitleText: '计划管理' } })

const plans = ref<FitnessPlan[]>([])
const exercises = ref<FitnessExercise[]>([])
const selectedPlanId = ref('')
const newPlanName = ref('')
const newExerciseName = ref('')
const newExerciseWeight = ref(0)
const newExerciseReps = ref(8)
const error = ref('')

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
  <view class="fitness-page pt-safe">
    <view class="fitness-shell">
      <view class="fitness-heading">
        <text class="fitness-eyebrow">FITNESS SETTINGS</text>
        <text class="fitness-title">计划与动作</text>
        <text class="fitness-subtitle">归档只影响今后的计划，过去的训练不会被删除。</text>
      </view>
      <text v-if="error" class="fitness-error">{{ error }}</text>

      <view class="fitness-section">
        <text class="fitness-section-title">训练计划</text>
        <view v-for="plan in plans" :key="plan.id" class="manage-row" :class="{ 'manage-selected': selectedPlanId === plan.id }">
          <input v-model="plan.name" class="fitness-input manage-name" @focus="selectPlan(plan.id)">
          <button class="fitness-secondary" @click="savePlan(plan)">
            保存
          </button>
          <button class="fitness-danger" @click="archivePlan(plan)">
            归档
          </button>
        </view>
        <view class="add-row">
          <input v-model="newPlanName" class="fitness-input" placeholder="新计划名称">
          <button class="fitness-secondary" @click="addPlan">
            新增计划
          </button>
        </view>
      </view>

      <view v-if="selectedPlanId" class="fitness-section">
        <text class="fitness-section-title">计划动作</text>
        <view v-for="(exercise, index) in exercises" :key="exercise.id" class="exercise-manage-row">
          <input v-model="exercise.name" class="fitness-input exercise-name">
          <input v-model.number="exercise.defaultWeight" class="fitness-input numeric-input" type="digit">
          <text class="field-unit">kg</text>
          <input v-model.number="exercise.defaultReps" class="fitness-input numeric-input" type="number">
          <text class="field-unit">次</text>
          <view class="manage-actions">
            <button class="fitness-icon-button" aria-label="上移" :disabled="index === 0" @click="moveExercise(index, -1)">
              ↑
            </button>
            <button class="fitness-icon-button" aria-label="下移" :disabled="index === exercises.length - 1" @click="moveExercise(index, 1)">
              ↓
            </button>
            <button class="fitness-secondary" @click="saveExercise(exercise)">
              保存
            </button>
            <button class="fitness-danger" @click="archiveExercise(exercise)">
              归档
            </button>
          </view>
        </view>
        <view class="new-exercise">
          <input v-model="newExerciseName" class="fitness-input" placeholder="动作名称">
          <view class="fitness-row" style="gap: 12rpx;">
            <input v-model.number="newExerciseWeight" class="fitness-input numeric-input" type="digit">
            <text class="field-unit">kg</text>
            <input v-model.number="newExerciseReps" class="fitness-input numeric-input" type="number">
            <text class="field-unit">次</text>
          </view>
          <button class="fitness-secondary" @click="addExercise">
            新增动作
          </button>
        </view>
      </view>
    </view>
  </view>
</template>

<style scoped lang="scss">
@import '@/modules/fitness/fitness.scss';

.manage-row,
.exercise-manage-row {
  display: grid;
  gap: 12rpx;
  padding: 22rpx 0;
  border-top: 1rpx solid #d5d3cc;
}

.manage-row {
  grid-template-columns: minmax(0, 1fr) auto auto;
}

.manage-row .fitness-secondary,
.manage-row .fitness-danger {
  grid-column: span 1;
}

.manage-selected {
  border-left: 5rpx solid #176b57;
  padding-left: 16rpx;
}

.exercise-manage-row {
  grid-template-columns: minmax(0, 1fr) 110rpx 40rpx 100rpx 40rpx;
}

.manage-actions {
  display: flex;
  grid-column: 1 / -1;
  flex-wrap: wrap;
  gap: 12rpx;
}

.numeric-input {
  text-align: center;
}

.field-unit {
  align-self: center;
  color: #777a73;
  font-size: 20rpx;
}

.add-row,
.new-exercise {
  display: grid;
  gap: 14rpx;
  padding-top: 26rpx;
}
</style>
