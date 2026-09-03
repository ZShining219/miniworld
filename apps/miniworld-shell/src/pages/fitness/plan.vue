<script lang="ts" setup>
import type { SessionDetail } from '@/modules/fitness'
import { fitnessApi, useFitnessStore, useFitnessWorkoutStatus } from '@/modules/fitness'
import ExerciseDefaultsFields from '@/modules/fitness/components/ExerciseDefaultsFields.vue'
import FitnessExerciseRow from '@/modules/fitness/components/FitnessExerciseRow.vue'
import FitnessPageShell from '@/modules/fitness/components/FitnessPageShell.vue'
import FitnessSectionHeader from '@/modules/fitness/components/FitnessSectionHeader.vue'

definePage({ style: { navigationBarTitleText: '本次训练' } })

const store = useFitnessStore()
const sessionId = ref('')
const session = ref<SessionDetail | null>(null)
const error = ref('')
const finishing = ref(false)
const managing = ref(false)
const adding = ref(false)
const newExerciseName = ref('')
const newExerciseWeight = ref(0)
const newExerciseReps = ref(8)
const { workoutStatus, workoutActionLabel, handleWorkoutAction } = useFitnessWorkoutStatus('plan')

onLoad((query) => {
  sessionId.value = String(query?.sessionId || '')
})

onShow(() => load())

async function load() {
  if (!sessionId.value)
    return
  error.value = ''
  try {
    session.value = await store.loadSession(sessionId.value)
  }
  catch {
    error.value = '无法读取本次训练，请检查连接后重试。'
  }
}

function openExercise(exerciseId: string) {
  uni.navigateTo({ url: `/pages/fitness/exercise?sessionId=${sessionId.value}&exerciseId=${exerciseId}` })
}

async function addExercise() {
  const name = newExerciseName.value.trim()
  if (!name || !session.value || adding.value)
    return
  adding.value = true
  error.value = ''
  try {
    await fitnessApi.createExercise({
      planId: session.value.planId,
      name,
      defaultWeight: newExerciseWeight.value,
      defaultReps: newExerciseReps.value,
    })
    newExerciseName.value = ''
    managing.value = false
    await load()
  }
  catch {
    error.value = '动作没有添加成功，输入已保留，请直接重试。'
  }
  finally {
    adding.value = false
  }
}

function requestFinish() {
  uni.showModal({
    title: '结束本次训练',
    content: '已完成的组会进入历史和统计。确认现在结束吗？',
    confirmText: '结束训练',
    success: async (result) => {
      if (!result.confirm || finishing.value)
        return
      finishing.value = true
      error.value = ''
      try {
        await store.finishSession(sessionId.value)
        uni.redirectTo({ url: '/pages/fitness/history' })
      }
      catch {
        error.value = '训练尚未结束，请稍后重试；已保存的组不会丢失。'
      }
      finally {
        finishing.value = false
      }
    },
  })
}
</script>

<template>
  <FitnessPageShell
    eyebrow="进行中的训练"
    :title="session?.planNameSnapshot || '训练'"
    :subtitle="`已完成 ${session?.totalSetCount || 0} 组，选择一个动作继续。`"
    :error="error"
    compact-heading
    :workout-status="workoutStatus"
    :workout-action-label="workoutActionLabel"
    @workout-action="handleWorkoutAction"
  >
    <template #heading>
      <text class="fitness-title">{{ session?.planNameSnapshot || '训练' }}</text>
      <view class="fitness-row-between active-heading-meta">
        <text class="fitness-subtitle">选择任意动作继续，不要求按列表顺序。</text>
        <text class="active-progress">{{ session?.totalSetCount || 0 }}<text class="active-progress-unit">组</text></text>
      </view>
    </template>

    <view class="fitness-section active-exercises-section">
      <FitnessSectionHeader title="本次动作" subtitle="点击动作进入组记录">
        <template #right>
          <wd-button class="manage-toggle" type="primary" variant="text" size="medium" @click="managing = !managing">
            {{ managing ? '收起' : '添加动作' }}
          </wd-button>
        </template>
      </FitnessSectionHeader>
      <FitnessExerciseRow
        v-for="item in session?.exercises || []"
        :key="item.exercise.id"
        :exercise="item.exercise"
        :meta="`今天已完成 ${item.completedSetCount} 组`"
        @select="openExercise(item.exercise.id)"
      />
      <view v-if="session && !session.exercises.length" class="fitness-empty-state">
        <wd-empty tip="本次训练还没有动作" icon-size="64" />
        <text class="fitness-note">添加动作后即可继续记录，不需要结束本次训练。</text>
        <wd-button class="empty-action" type="primary" variant="soft" size="large" block @click="managing = true">
          添加动作继续
        </wd-button>
      </view>
      <view v-if="managing" class="active-add-panel">
        <text class="active-add-title">添加到当前计划</text>
        <ExerciseDefaultsFields
          v-model:name="newExerciseName"
          v-model:weight="newExerciseWeight"
          v-model:reps="newExerciseReps"
          name-placeholder="例如：绳索下压"
        >
          <template #action>
            <wd-button class="fitness-primary" type="primary" size="large" block :loading="adding" :disabled="adding || !newExerciseName.trim()" @click="addExercise">
              保存动作
            </wd-button>
          </template>
        </ExerciseDefaultsFields>
        <text class="active-safe-note">这里只追加动作，不会删除计划或历史记录。</text>
      </view>
    </view>

    <view class="fitness-danger-zone">
      <text class="fitness-danger-label">结束训练</text>
      <text class="fitness-note">结束后本次训练会进入历史和统计，仍需再次确认。</text>
      <wd-button class="fitness-danger finish-button" type="danger" variant="plain" size="large" :loading="finishing" :disabled="finishing" @click="requestFinish">
        结束本次训练
      </wd-button>
    </view>
  </FitnessPageShell>
</template>

<style scoped lang="scss">
.active-heading-meta {
  align-items: flex-end;
  gap: var(--mw-space-4);
}

.active-heading-meta .fitness-subtitle {
  flex: 1;
}

.active-progress {
  flex: none;
  color: var(--mw-color-primary);
  font-size: var(--mw-font-data);
  font-weight: 700;
  line-height: 1;
}

.active-progress-unit {
  margin-left: var(--mw-space-1);
  color: var(--mw-color-text-secondary);
  font-size: var(--mw-font-auxiliary);
  font-weight: 400;
}

.active-exercises-section {
  padding-top: var(--mw-space-5);
}

.active-add-panel {
  margin-top: var(--mw-space-5);
  padding: var(--mw-space-4);
  border: 1px solid var(--mw-color-border);
  border-radius: var(--mw-radius-md);
  background: var(--mw-color-surface-muted);
}

.active-add-title {
  display: block;
  margin-bottom: var(--mw-space-3);
  font-size: var(--mw-font-strong);
  font-weight: 700;
}

.active-safe-note {
  display: block;
  margin-top: var(--mw-space-3);
  color: var(--mw-color-text-muted);
  font-size: var(--mw-font-auxiliary);
  line-height: 1.5;
}

.empty-action,
.finish-button {
  width: 100%;
  margin-top: var(--mw-space-4);
}
</style>
