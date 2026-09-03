<script lang="ts" setup>
import type { FitnessExercise, FitnessPlan } from '@/modules/fitness'
import { fitnessApi, useFitnessWorkoutStatus } from '@/modules/fitness'
import ExerciseDefaultsFields from '@/modules/fitness/components/ExerciseDefaultsFields.vue'
import FitnessChoiceChips from '@/modules/fitness/components/FitnessChoiceChips.vue'
import FitnessExerciseEditorRow from '@/modules/fitness/components/FitnessExerciseEditorRow.vue'
import FitnessExerciseRow from '@/modules/fitness/components/FitnessExerciseRow.vue'
import FitnessPageShell from '@/modules/fitness/components/FitnessPageShell.vue'
import FitnessPlanEditorRow from '@/modules/fitness/components/FitnessPlanEditorRow.vue'
import FitnessSectionHeader from '@/modules/fitness/components/FitnessSectionHeader.vue'

definePage({ style: { navigationBarTitleText: '计划管理' } })

const plans = ref<FitnessPlan[]>([])
const exercises = ref<FitnessExercise[]>([])
const selectedPlanId = ref('')
const editingExerciseId = ref('')
const addingPlan = ref(false)
const addingExercise = ref(false)
const busy = ref(false)
const loading = ref(true)
const newPlanName = ref('')
const newExerciseName = ref('')
const newExerciseWeight = ref(0)
const newExerciseReps = ref(8)
const error = ref('')
const savedNotice = ref('')
const { workoutStatus, workoutActionLabel, handleWorkoutAction } = useFitnessWorkoutStatus('other')

const selectedPlan = computed(() => plans.value.find(plan => plan.id === selectedPlanId.value) || null)

onLoad(() => loadPlans())

function announceSaved(message: string) {
  savedNotice.value = message
  setTimeout(() => {
    savedNotice.value = ''
  }, 2200)
}

async function loadPlans(preferredId?: string) {
  loading.value = true
  error.value = ''
  try {
    plans.value = await fitnessApi.listPlans()
    const id = preferredId || selectedPlanId.value || plans.value[0]?.id
    if (id)
      await selectPlan(id)
    else
      exercises.value = []
  }
  catch {
    error.value = '计划读取失败，请检查连接后重试。'
  }
  finally {
    loading.value = false
  }
}

async function selectPlan(planId: string) {
  selectedPlanId.value = planId
  editingExerciseId.value = ''
  addingExercise.value = false
  exercises.value = await fitnessApi.listExercises(planId)
}

async function addPlan() {
  const name = newPlanName.value.trim()
  if (!name || busy.value)
    return
  busy.value = true
  error.value = ''
  try {
    const plan = await fitnessApi.createPlan({ name })
    newPlanName.value = ''
    addingPlan.value = false
    await loadPlans(plan.id)
    announceSaved('计划已创建')
  }
  catch {
    error.value = '计划没有创建成功，输入已保留。'
  }
  finally {
    busy.value = false
  }
}

async function savePlan(plan: FitnessPlan) {
  if (busy.value)
    return
  busy.value = true
  error.value = ''
  try {
    await fitnessApi.updatePlan(plan.id, { name: plan.name })
    await loadPlans(plan.id)
    announceSaved('计划名称已保存')
  }
  catch {
    error.value = '计划名称没有保存成功，请重试。'
  }
  finally {
    busy.value = false
  }
}

function archivePlan(plan: FitnessPlan) {
  uni.showModal({
    title: `归档“${plan.name}”`,
    content: '计划将不再出现在训练首页，过去的训练历史不会被删除。',
    confirmText: '确认归档',
    success: async (result) => {
      if (!result.confirm || busy.value)
        return
      busy.value = true
      error.value = ''
      try {
        await fitnessApi.archivePlan(plan.id)
        selectedPlanId.value = ''
        await loadPlans()
      }
      catch {
        error.value = '进行中的训练计划不能归档，请先结束训练。'
      }
      finally {
        busy.value = false
      }
    },
  })
}

async function addExercise() {
  const name = newExerciseName.value.trim()
  if (!name || !selectedPlanId.value || busy.value)
    return
  busy.value = true
  error.value = ''
  try {
    await fitnessApi.createExercise({
      planId: selectedPlanId.value,
      name,
      defaultWeight: newExerciseWeight.value,
      defaultReps: newExerciseReps.value,
    })
    newExerciseName.value = ''
    addingExercise.value = false
    await selectPlan(selectedPlanId.value)
    announceSaved('动作已添加')
  }
  catch {
    error.value = '动作没有添加成功，输入已保留。'
  }
  finally {
    busy.value = false
  }
}

async function saveExercise(exercise: FitnessExercise) {
  if (busy.value)
    return
  busy.value = true
  error.value = ''
  try {
    await fitnessApi.updateExercise(exercise.id, {
      name: exercise.name,
      defaultWeight: exercise.defaultWeight,
      defaultReps: exercise.defaultReps,
    })
    await selectPlan(selectedPlanId.value)
    announceSaved('动作设置已保存')
  }
  catch {
    error.value = '动作设置没有保存成功，请重试。'
  }
  finally {
    busy.value = false
  }
}

function archiveExercise(exercise: FitnessExercise) {
  uni.showModal({
    title: `归档“${exercise.name}”`,
    content: '动作将从今后的计划中移除，过去的组记录会继续保留。',
    confirmText: '确认归档',
    success: async (result) => {
      if (!result.confirm || busy.value)
        return
      busy.value = true
      error.value = ''
      try {
        await fitnessApi.archiveExercise(exercise.id)
        await selectPlan(selectedPlanId.value)
      }
      catch {
        error.value = '动作没有归档成功，请稍后重试。'
      }
      finally {
        busy.value = false
      }
    },
  })
}

async function moveExercise(index: number, direction: number) {
  const target = index + direction
  if (target < 0 || target >= exercises.value.length || busy.value)
    return
  const reordered = [...exercises.value]
  ;[reordered[index], reordered[target]] = [reordered[target], reordered[index]]
  busy.value = true
  error.value = ''
  try {
    exercises.value = await fitnessApi.reorderExercises(selectedPlanId.value, reordered.map(item => item.id))
  }
  catch {
    error.value = '动作顺序没有保存成功，请重试。'
  }
  finally {
    busy.value = false
  }
}
</script>

<template>
  <FitnessPageShell
    eyebrow="训练设置"
    title="计划与动作"
    subtitle="选择一项后再编辑，避免在手机上堆叠过多表单。"
    :error="error"
    :workout-status="workoutStatus"
    :workout-action-label="workoutActionLabel"
    @workout-action="handleWorkoutAction"
  >
    <text v-if="savedNotice" class="settings-saved" role="status">✓ {{ savedNotice }}</text>

    <view class="fitness-section">
      <FitnessSectionHeader title="训练计划" subtitle="先选择要管理的计划">
        <template #right>
          <wd-button type="primary" variant="text" size="medium" @click="addingPlan = !addingPlan">
            {{ addingPlan ? '收起' : '新建计划' }}
          </wd-button>
        </template>
      </FitnessSectionHeader>
      <view v-if="loading" class="fitness-loading-state">
        <wd-loading size="22px" />
      </view>
      <view v-else-if="!plans.length" class="fitness-empty-state">
        <wd-empty tip="还没有训练计划" icon-size="64" />
      </view>
      <FitnessChoiceChips v-else :items="plans" :model-value="selectedPlanId" label="选择训练计划" @select="selectPlan" />

      <view v-if="addingPlan" class="settings-form-panel">
        <text class="settings-field-label">新计划名称</text>
        <wd-input v-model="newPlanName" class="fitness-input" placeholder="例如：肩部训练" clearable />
        <wd-button class="fitness-primary settings-submit" type="primary" size="large" block :loading="busy" :disabled="busy || !newPlanName.trim()" @click="addPlan">
          创建计划
        </wd-button>
      </view>

      <FitnessPlanEditorRow
        v-if="selectedPlan"
        class="selected-plan-editor"
        :plan="selectedPlan"
        selected
        @update:name="selectedPlan.name = $event"
        @save="savePlan(selectedPlan)"
        @archive="archivePlan(selectedPlan)"
      />
    </view>

    <view v-if="selectedPlanId" class="fitness-section">
      <FitnessSectionHeader title="计划动作" subtitle="点击编辑后才展开动作表单">
        <template #right>
          <wd-button type="primary" variant="text" size="medium" @click="addingExercise = !addingExercise">
            {{ addingExercise ? '收起' : '添加动作' }}
          </wd-button>
        </template>
      </FitnessSectionHeader>

      <view v-if="!exercises.length" class="fitness-empty-state">
        <wd-empty tip="这个计划还没有动作" icon-size="64" />
      </view>
      <template v-for="(exercise, index) in exercises" :key="exercise.id">
        <FitnessExerciseRow
          v-if="editingExerciseId !== exercise.id"
          :exercise="exercise"
          :meta="`${exercise.defaultWeight} kg × ${exercise.defaultReps} 次`"
          action-label="编辑"
          action-aria-label="编辑动作"
          action-tone="primary"
          :disabled="busy"
          @select="editingExerciseId = exercise.id"
          @action="editingExerciseId = exercise.id"
        />
        <view v-else class="settings-form-panel exercise-editor-panel">
          <FitnessExerciseEditorRow
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
          <wd-button type="info" variant="text" size="medium" @click="editingExerciseId = ''">
            取消编辑
          </wd-button>
        </view>
      </template>

      <view v-if="addingExercise" class="settings-form-panel">
        <ExerciseDefaultsFields v-model:name="newExerciseName" v-model:weight="newExerciseWeight" v-model:reps="newExerciseReps">
          <template #action>
            <wd-button class="fitness-primary" type="primary" size="large" block :loading="busy" :disabled="busy || !newExerciseName.trim()" @click="addExercise">
              保存动作
            </wd-button>
          </template>
        </ExerciseDefaultsFields>
      </view>
      <text class="fitness-note settings-history-note">归档只影响今后的计划，过去的训练记录不会删除。</text>
    </view>
  </FitnessPageShell>
</template>

<style scoped lang="scss">
.settings-saved {
  display: block;
  margin-bottom: var(--mw-space-4);
  padding: var(--mw-space-3) var(--mw-space-4);
  border-radius: var(--mw-radius-md);
  color: var(--mw-color-success);
  background: var(--mw-color-primary-soft);
  font-size: var(--mw-font-body);
  font-weight: 700;
}

.settings-form-panel {
  margin-top: var(--mw-space-4);
  padding: var(--mw-space-4);
  border: 1px solid var(--mw-color-border);
  border-radius: var(--mw-radius-md);
  background: var(--mw-color-surface-muted);
}

.settings-field-label {
  display: block;
  margin-bottom: var(--mw-space-2);
  color: var(--mw-color-text-secondary);
  font-size: var(--mw-font-body);
  font-weight: 650;
}

.settings-submit,
.settings-history-note {
  margin-top: var(--mw-space-4);
}

.selected-plan-editor {
  margin-top: var(--mw-space-4);
}

.exercise-editor-panel :deep(.exercise-editor-row) {
  padding-top: 0;
  border-top: 0;
}
</style>
