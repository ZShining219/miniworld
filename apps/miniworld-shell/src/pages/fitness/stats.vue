<script lang="ts" setup>
import type { ExerciseProgress, FitnessExercise, FitnessPlan, ProgressMode } from '@/modules/fitness'
import FitnessChoiceChips from '@/modules/fitness/components/FitnessChoiceChips.vue'
import FitnessPageShell from '@/modules/fitness/components/FitnessPageShell.vue'
import FitnessProgressChart from '@/modules/fitness/components/FitnessProgressChart.vue'
import type { ProgressChartType } from '@/modules/fitness/components/progressChart'
import { fitnessApi, useFitnessWorkoutStatus } from '@/modules/fitness'

definePage({ style: { navigationBarTitleText: '训练统计' } })

const plans = ref<FitnessPlan[]>([])
const exercises = ref<FitnessExercise[]>([])
const selectedPlanId = ref('')
const selectedExerciseId = ref('')
const trainedDates = ref<string[]>([])
const progress = ref<ExerciseProgress | null>(null)
const progressMode = ref<ProgressMode>('day')
const chartType = ref<ProgressChartType>('line')
const error = ref('')
const { workoutStatus, workoutActionLabel, handleWorkoutAction } = useFitnessWorkoutStatus('other')

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
  progress.value = await fitnessApi.progress(exerciseId, progressMode.value)
}

async function selectProgressMode(mode: ProgressMode) {
  progressMode.value = mode
  if (selectedExerciseId.value)
    progress.value = await fitnessApi.progress(selectedExerciseId.value, mode)
}

function cellDate(day: number) {
  return `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`
}
</script>

<template>
  <FitnessPageShell
    eyebrow="TRAINING STATS"
    title="训练统计"
    subtitle="打卡按已结束训练计算；趋势可按训练日或每组查看。"
    :error="error"
    :workout-status="workoutStatus"
    :workout-action-label="workoutActionLabel"
    @workout-action="handleWorkoutAction"
  >
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
      <FitnessChoiceChips class="plan-chips" :items="plans" :model-value="selectedPlanId" label="选择训练部位" @select="selectPlan" />
      <FitnessChoiceChips class="exercise-chips" :items="exercises" :model-value="selectedExerciseId" label="选择训练动作" @select="selectExercise" />
      <view class="chart-controls" role="group" aria-label="趋势粒度">
        <button class="chart-control" :class="{ 'chart-control-active': progressMode === 'day' }" :aria-pressed="progressMode === 'day'" @click="selectProgressMode('day')">
          按天
        </button>
        <button class="chart-control" :class="{ 'chart-control-active': progressMode === 'set' }" :aria-pressed="progressMode === 'set'" @click="selectProgressMode('set')">
          按次数
        </button>
      </view>
      <view class="chart-controls" role="group" aria-label="图表类型">
        <button class="chart-control" :class="{ 'chart-control-active': chartType === 'line' }" :aria-pressed="chartType === 'line'" @click="chartType = 'line'">
          折线
        </button>
        <button class="chart-control" :class="{ 'chart-control-active': chartType === 'bar' }" :aria-pressed="chartType === 'bar'" @click="chartType = 'bar'">
          柱状
        </button>
      </view>
      <FitnessProgressChart :progress="progress" :mode="progressMode" :chart-type="chartType" />
      <text v-if="progress?.points.length" class="fitness-meta">{{ progressMode === 'day' ? '按训练日显示平均重量' : '按完成顺序显示每组重量' }}</text>
    </view>
  </FitnessPageShell>
</template>

<style scoped lang="scss">
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

.chart-controls {
  display: flex;
  gap: 12rpx;
  margin-bottom: 14rpx;
}

.chart-control {
  min-width: 112rpx;
  min-height: 64rpx;
  padding: 0 20rpx;
  border: 1rpx solid #aaa9a2;
  border-radius: 2rpx;
  color: #50544f;
  background: transparent;
  font-size: 21rpx;
}

.chart-control-active {
  border-color: #176b57;
  color: #fff;
  background: #176b57;
}
</style>
