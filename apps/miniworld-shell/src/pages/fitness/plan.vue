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
  try {
    session.value = await store.loadSession(sessionId.value)
  }
  catch {
    error.value = '无法读取本次训练。'
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
    await load()
  }
  catch {
    error.value = '动作没有添加成功，请稍后重试。'
  }
  finally {
    adding.value = false
  }
}

function requestFinish() {
  uni.showModal({
    title: '结束本次训练',
    content: '已完成的组会进入历史和统计。',
    confirmText: '结束训练',
    success: async (result) => {
      if (!result.confirm || finishing.value)
        return
      finishing.value = true
      try {
        await store.finishSession(sessionId.value)
        uni.redirectTo({ url: '/pages/fitness/history' })
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
    eyebrow="ACTIVE WORKOUT"
    :title="session?.planNameSnapshot || '训练'"
    :subtitle="`已完成 ${session?.totalSetCount || 0} 组。可按任意顺序选择动作。`"
    :error="error"
    compact-heading
    :workout-status="workoutStatus"
    :workout-action-label="workoutActionLabel"
    @workout-action="handleWorkoutAction"
  >
    <template #heading>
      <text class="fitness-title">{{ session?.planNameSnapshot || '训练' }}</text>
      <view class="fitness-row-between active-heading-meta">
        <text class="fitness-subtitle">已完成 {{ session?.totalSetCount || 0 }} 组。可按任意顺序选择动作。</text>
        <text class="active-progress">{{ session?.totalSetCount || 0 }}<text class="active-progress-unit">组</text></text>
      </view>
    </template>

    <view class="fitness-section active-exercises-section">
      <FitnessSectionHeader title="本次动作" subtitle="选择任意动作继续，不要求按列表顺序">
        <template #right>
          <button class="manage-toggle" @click="managing = !managing">
            {{ managing ? '收起' : '管理' }}
          </button>
        </template>
      </FitnessSectionHeader>
      <FitnessExerciseRow
        v-for="item in session?.exercises || []"
        :key="item.exercise.id"
        :exercise="item.exercise"
        :meta="`今天 ${item.completedSetCount} 组`"
        @select="openExercise(item.exercise.id)"
      />
      <text v-if="session && !session.exercises.length" class="fitness-empty">该计划还没有动作，先添加一个再继续。</text>
      <view v-if="managing" class="active-add-panel">
        <text class="active-add-title">增加动作</text>
        <ExerciseDefaultsFields
          v-model:name="newExerciseName"
          v-model:weight="newExerciseWeight"
          v-model:reps="newExerciseReps"
          name-placeholder="例如：绳索下压"
        >
          <template #action>
            <button class="fitness-secondary" :disabled="adding" @click="addExercise">
              {{ adding ? '添加中' : '添加' }}
            </button>
          </template>
        </ExerciseDefaultsFields>
        <text class="active-safe-note">训练中的动作只支持追加，不会从计划或历史记录中删除。</text>
      </view>
    </view>

    <view class="fitness-section">
      <button class="fitness-danger" :disabled="finishing" @click="requestFinish">
        {{ finishing ? '正在结束…' : '结束本次训练' }}
      </button>
    </view>
  </FitnessPageShell>
</template>

<style scoped lang="scss">
.active-heading-meta {
  align-items: flex-end;
  gap: 16rpx;
}

.active-heading-meta .fitness-subtitle {
  flex: 1;
}

.active-progress {
  flex: none;
  color: #176b57;
  font-family: Georgia, serif;
  font-size: 48rpx;
  font-weight: 700;
  line-height: 1;
}

.active-progress-unit {
  margin-left: 4rpx;
  color: #777a73;
  font-family: 'PingFang SC', sans-serif;
  font-size: 18rpx;
  font-weight: 400;
}

.active-exercises-section {
  padding-top: 32rpx;
}

.manage-toggle {
  min-height: 54rpx;
  padding: 0 18rpx;
  border: 1rpx solid #aaa9a2;
  border-radius: 2rpx;
  color: #176b57;
  background: transparent;
  font-size: 20rpx;
  line-height: 52rpx;
}

.active-add-panel {
  margin-top: 24rpx;
  padding: 22rpx;
  border: 1rpx solid #c8c8c0;
  background: #ebece6;
}

.active-add-title {
  display: block;
  margin-bottom: 14rpx;
  color: #1d2420;
  font-size: 23rpx;
  font-weight: 700;
}

.active-safe-note {
  display: block;
  margin-top: 16rpx;
  color: #777a73;
  font-size: 18rpx;
  line-height: 1.5;
}
</style>
