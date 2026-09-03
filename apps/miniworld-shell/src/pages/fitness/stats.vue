<script lang="ts" setup>
import type { ExerciseProgress, FitnessExercise, FitnessPlan, ProgressMode } from '@/modules/fitness'
import FitnessChoiceChips from '@/modules/fitness/components/FitnessChoiceChips.vue'
import FitnessPageShell from '@/modules/fitness/components/FitnessPageShell.vue'
import FitnessProgressChart from '@/modules/fitness/components/FitnessProgressChart.vue'
import FitnessSectionHeader from '@/modules/fitness/components/FitnessSectionHeader.vue'
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
const loading = ref(true)
const { workoutStatus, workoutActionLabel, handleWorkoutAction } = useFitnessWorkoutStatus('other')

const progressModeItems = [
  { id: 'day', name: '按训练日' },
  { id: 'set', name: '按每组' },
]
const chartTypeItems = [
  { id: 'line', name: '折线' },
  { id: 'bar', name: '柱状' },
]

const now = new Date()
const year = now.getFullYear()
const month = now.getMonth()
const start = `${year}-${String(month + 1).padStart(2, '0')}-01`
const endDate = new Date(year, month + 1, 0)
const end = `${year}-${String(month + 1).padStart(2, '0')}-${String(endDate.getDate()).padStart(2, '0')}`
const leading = new Date(year, month, 1).getDay()
const calendarCells = Array.from({ length: leading + endDate.getDate() }, (_, index) => index < leading ? null : index - leading + 1)

onLoad(async () => {
  loading.value = true
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
  finally {
    loading.value = false
  }
})

async function selectPlan(planId: string) {
  error.value = ''
  try {
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
  catch {
    error.value = '动作统计读取失败，请稍后重试。'
  }
}

async function selectExercise(exerciseId: string) {
  error.value = ''
  try {
    selectedExerciseId.value = exerciseId
    progress.value = await fitnessApi.progress(exerciseId, progressMode.value)
  }
  catch {
    error.value = '重量趋势读取失败，请稍后重试。'
  }
}

async function selectProgressMode(mode: string) {
  const selectedMode = mode as ProgressMode
  progressMode.value = selectedMode
  if (selectedExerciseId.value)
    progress.value = await fitnessApi.progress(selectedExerciseId.value, selectedMode)
}

function selectChartType(type: string) {
  chartType.value = type as ProgressChartType
}

function cellDate(day: number) {
  return `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`
}
</script>

<template>
  <FitnessPageShell
    eyebrow="训练数据"
    title="训练统计"
    subtitle="打卡按已结束训练计算；趋势可按训练日或每组查看。"
    :error="error"
    :workout-status="workoutStatus"
    :workout-action-label="workoutActionLabel"
    @workout-action="handleWorkoutAction"
  >
    <view v-if="loading" class="fitness-card fitness-loading-state">
      <wd-loading size="22px" />
      <text class="fitness-meta">正在整理训练数据</text>
    </view>

    <view v-else class="fitness-section">
      <FitnessSectionHeader :title="`${year} 年 ${month + 1} 月`" subtitle="仅统计已经结束的训练">
        <template #right>
          <text class="calendar-count">{{ trainedDates.length }}<text> 天</text></text>
        </template>
      </FitnessSectionHeader>
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

    <view v-if="!loading" class="fitness-section">
      <FitnessSectionHeader title="动作重量趋势" subtitle="选择部位、动作和统计方式" />
      <FitnessChoiceChips class="plan-chips" :items="plans" :model-value="selectedPlanId" label="选择训练部位" @select="selectPlan" />
      <FitnessChoiceChips class="exercise-chips" :items="exercises" :model-value="selectedExerciseId" label="选择训练动作" @select="selectExercise" />
      <view class="chart-options">
        <view>
          <text class="chart-option-label">统计方式</text>
          <FitnessChoiceChips :items="progressModeItems" :model-value="progressMode" label="趋势粒度" @select="selectProgressMode" />
        </view>
        <view>
          <text class="chart-option-label">图表样式</text>
          <FitnessChoiceChips :items="chartTypeItems" :model-value="chartType" label="图表类型" @select="selectChartType" />
        </view>
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
  padding-bottom: var(--mw-space-2);
  color: var(--mw-color-text-muted);
  font-size: var(--mw-font-auxiliary);
  text-align: center;
}

.calendar-cell {
  display: flex;
  aspect-ratio: 1;
  align-items: center;
  justify-content: center;
  color: var(--mw-color-text-secondary);
  font-size: var(--mw-font-body);
  font-variant-numeric: tabular-nums;
}

.calendar-trained {
  border-radius: var(--mw-radius-pill);
  color: var(--mw-color-surface);
  background: var(--mw-color-primary);
  box-shadow: inset 0 0 0 var(--mw-space-1) var(--mw-color-surface);
}

.plan-chips {
  margin-bottom: var(--mw-space-3);
}

.exercise-chips {
  margin-bottom: var(--mw-space-5);
}

.chart-options {
  display: grid;
  gap: var(--mw-space-4);
  margin-bottom: var(--mw-space-5);
  padding: var(--mw-space-4);
  border-radius: var(--mw-radius-md);
  background: var(--mw-color-surface-muted);
}

.chart-option-label {
  display: block;
  margin-bottom: var(--mw-space-2);
  color: var(--mw-color-text-secondary);
  font-size: var(--mw-font-body);
  font-weight: 650;
}

.calendar-count {
  color: var(--mw-color-primary);
  font-size: var(--mw-font-section);
  font-weight: 700;
}

.calendar-count text {
  font-size: var(--mw-font-auxiliary);
}
</style>
