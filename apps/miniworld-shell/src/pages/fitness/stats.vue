<script lang="ts" setup>
import type { ExerciseProgress, FitnessExercise, FitnessPlan } from '@/modules/fitness'
import ProgressChart from '@/modules/fitness/components/ProgressChart.vue'
import { fitnessApi } from '@/modules/fitness'

definePage({ style: { navigationBarTitleText: '训练统计' } })

const plans = ref<FitnessPlan[]>([])
const exercises = ref<FitnessExercise[]>([])
const selectedPlanId = ref('')
const selectedExerciseId = ref('')
const trainedDates = ref<string[]>([])
const progress = ref<ExerciseProgress | null>(null)
const error = ref('')

const now = new Date()
const year = now.getFullYear()
const month = now.getMonth()
const start = `${year}-${String(month + 1).padStart(2, '0')}-01`
const endDate = new Date(year, month + 1, 0)
const end = `${year}-${String(month + 1).padStart(2, '0')}-${String(endDate.getDate()).padStart(2, '0')}`
const leading = new Date(year, month, 1).getDay()
const calendarCells = Array.from({ length: leading + endDate.getDate() }, (_, index) => index < leading ? null : index - leading + 1)

onLoad(async () => {
  try {
    const [planValues, calendar] = await Promise.all([
      fitnessApi.listPlans(),
      fitnessApi.calendar(start, end),
    ])
    plans.value = planValues
    trainedDates.value = calendar.dates
    if (plans.value[0])
      await selectPlan(plans.value[0].id)
  }
  catch {
    error.value = '暂时无法读取训练统计。'
  }
})

async function selectPlan(planId: string) {
  selectedPlanId.value = planId
  exercises.value = await fitnessApi.listExercises(planId)
  if (exercises.value[0]) {
    await selectExercise(exercises.value[0].id)
  }
  else {
    selectedExerciseId.value = ''
    progress.value = null
  }
}

async function selectExercise(exerciseId: string) {
  selectedExerciseId.value = exerciseId
  progress.value = await fitnessApi.progress(exerciseId)
}

function cellDate(day: number) {
  return `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`
}
</script>

<template>
  <view class="fitness-page pt-safe">
    <view class="fitness-shell">
      <view class="fitness-heading">
        <text class="fitness-eyebrow">TRAINING STATS</text>
        <text class="fitness-title">训练统计</text>
        <text class="fitness-subtitle">打卡按已结束训练计算；趋势显示每次训练的最大重量。</text>
      </view>
      <text v-if="error" class="fitness-error">{{ error }}</text>

      <view class="fitness-section">
        <text class="fitness-section-title">{{ year }} 年 {{ month + 1 }} 月</text>
        <view class="calendar-week">
          <text v-for="label in ['日', '一', '二', '三', '四', '五', '六']" :key="label">{{ label }}</text>
        </view>
        <view class="calendar-grid">
          <view
            v-for="(day, index) in calendarCells"
            :key="index"
            class="calendar-cell"
            :class="{ 'calendar-trained': day && trainedDates.includes(cellDate(day)) }"
          >
            <text v-if="day">{{ day }}</text>
          </view>
        </view>
      </view>

      <view class="fitness-section">
        <text class="fitness-section-title">动作重量趋势</text>
        <view class="fitness-chip-list plan-chips">
          <button
            v-for="plan in plans"
            :key="plan.id"
            class="fitness-chip"
            :class="{ 'fitness-chip-active': selectedPlanId === plan.id }"
            @click="selectPlan(plan.id)"
          >
            {{ plan.name }}
          </button>
        </view>
        <view class="fitness-chip-list exercise-chips">
          <button
            v-for="exercise in exercises"
            :key="exercise.id"
            class="fitness-chip"
            :class="{ 'fitness-chip-active': selectedExerciseId === exercise.id }"
            @click="selectExercise(exercise.id)"
          >
            {{ exercise.name }}
          </button>
        </view>
        <ProgressChart :points="progress?.points || []" />
        <text v-if="progress?.points.length" class="fitness-meta">最近最大重量 {{ progress.points[progress.points.length - 1].maxWeight }} kg</text>
      </view>
    </view>
  </view>
</template>

<style scoped lang="scss">
@import '@/modules/fitness/fitness.scss';

.calendar-week,
.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
}

.calendar-week {
  padding-bottom: 12rpx;
  color: #777a73;
  font-size: 18rpx;
  text-align: center;
}

.calendar-cell {
  display: flex;
  aspect-ratio: 1;
  align-items: center;
  justify-content: center;
  border-top: 1rpx solid #d5d3cc;
  color: #555a54;
  font-family: Georgia, serif;
  font-size: 21rpx;
}

.calendar-trained {
  color: #fff;
  background: #176b57;
}

.plan-chips {
  margin-bottom: 16rpx;
}

.exercise-chips {
  margin-bottom: 30rpx;
}
</style>
