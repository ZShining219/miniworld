<script setup lang="ts">
import type { CSSProperties } from 'vue'
import type { FitnessPlan } from '@/modules/fitness'
import { getCurrentInstance, onBeforeUnmount, ref, watch } from 'vue'
import FitnessPlanCard from './FitnessPlanCard.vue'
import { hasSameOrder, moveItem } from './planOrder'

interface TouchPoint {
  clientY: number
}

interface TouchLikeEvent {
  touches?: TouchPoint[]
  changedTouches?: TouchPoint[]
  preventDefault?: () => void
  stopPropagation?: () => void
}

interface CardRect {
  top: number
  height: number
}

const props = withDefaults(defineProps<{
  plans: FitnessPlan[]
  disabled?: boolean
}>(), { disabled: false })

const emit = defineEmits<{
  select: [plan: FitnessPlan]
  reorder: [ids: string[]]
}>()

const LONG_PRESS_MS = 350
const SCROLL_TOLERANCE_PX = 8

const candidateId = ref('')
const draggingId = ref('')
const originIndex = ref(-1)
const targetIndex = ref(-1)
const startY = ref(0)
const currentY = ref(0)
const cardRects = ref<CardRect[]>([])
const suppressClickUntil = ref(0)
let longPressTimer: ReturnType<typeof setTimeout> | undefined
const componentInstance = getCurrentInstance()

function pointFrom(event: TouchLikeEvent): TouchPoint | undefined {
  return event.touches?.[0] || event.changedTouches?.[0]
}

function clearTimer() {
  if (longPressTimer)
    clearTimeout(longPressTimer)
  longPressTimer = undefined
}

function resetDrag(suppressClick = false) {
  clearTimer()
  if (suppressClick)
    suppressClickUntil.value = Date.now() + 500
  candidateId.value = ''
  draggingId.value = ''
  originIndex.value = -1
  targetIndex.value = -1
  cardRects.value = []
}

function measureCards(): Promise<CardRect[]> {
  return new Promise((resolve) => {
    const query = uni.createSelectorQuery()
    if (componentInstance?.proxy)
      query.in(componentInstance.proxy)
    query
      .selectAll('.plan-sort-item')
      .boundingClientRect(rects => resolve((rects || []) as unknown as CardRect[]))
      .exec()
  })
}

async function activateDrag(plan: FitnessPlan, index: number) {
  if (candidateId.value !== plan.id || props.disabled)
    return
  draggingId.value = plan.id
  originIndex.value = index
  targetIndex.value = index
  cardRects.value = await measureCards()
  if (candidateId.value !== plan.id) {
    resetDrag()
    return
  }
  uni.vibrateShort?.({ type: 'light' })
}

function onTouchStart(event: TouchLikeEvent, plan: FitnessPlan, index: number) {
  if (props.disabled || props.plans.length < 2)
    return
  const point = pointFrom(event)
  if (!point)
    return
  resetDrag()
  candidateId.value = plan.id
  originIndex.value = index
  targetIndex.value = index
  startY.value = point.clientY
  currentY.value = point.clientY
  longPressTimer = setTimeout(() => activateDrag(plan, index), LONG_PRESS_MS)
}

function findTargetIndex(deltaY: number): number {
  if (!cardRects.value.length)
    return originIndex.value
  const originRect = cardRects.value[originIndex.value]
  if (!originRect)
    return originIndex.value
  const draggedCenter = originRect.top + originRect.height / 2 + deltaY
  let target = originIndex.value
  if (deltaY > 0) {
    for (let index = originIndex.value + 1; index < cardRects.value.length; index += 1) {
      const rect = cardRects.value[index]
      if (draggedCenter <= rect.top + rect.height / 2)
        break
      target = index
    }
  }
  else if (deltaY < 0) {
    for (let index = originIndex.value - 1; index >= 0; index -= 1) {
      const rect = cardRects.value[index]
      if (draggedCenter >= rect.top + rect.height / 2)
        break
      target = index
    }
  }
  return target
}

function onTouchMove(event: TouchLikeEvent) {
  const point = pointFrom(event)
  if (!point || !candidateId.value)
    return

  currentY.value = point.clientY
  if (!draggingId.value) {
    if (Math.abs(currentY.value - startY.value) > SCROLL_TOLERANCE_PX)
      resetDrag(true)
    return
  }

  event.preventDefault?.()
  event.stopPropagation?.()
  targetIndex.value = findTargetIndex(currentY.value - startY.value)
}

function onTouchEnd() {
  if (!candidateId.value)
    return
  const wasDragging = Boolean(draggingId.value)
  if (wasDragging && originIndex.value !== targetIndex.value) {
    const reordered = moveItem(props.plans, originIndex.value, targetIndex.value)
    const currentIds = props.plans.map(plan => plan.id)
    const reorderedIds = reordered.map(plan => plan.id)
    if (!hasSameOrder(currentIds, reorderedIds))
      emit('reorder', reorderedIds)
  }
  resetDrag(wasDragging)
}

function selectPlan(plan: FitnessPlan) {
  if (props.disabled || draggingId.value || Date.now() < suppressClickUntil.value)
    return
  emit('select', plan)
}

function slotDistance(): number {
  const index = originIndex.value
  const rects = cardRects.value
  if (index >= 0 && rects[index + 1])
    return rects[index + 1].top - rects[index].top
  if (index > 0 && rects[index - 1])
    return rects[index].top - rects[index - 1].top
  return rects[index]?.height || 0
}

function itemStyle(plan: FitnessPlan, index: number): CSSProperties {
  if (!draggingId.value)
    return {}
  if (plan.id === draggingId.value) {
    return {
      transform: `translate3d(0, ${currentY.value - startY.value}px, 0) scale(1.015)`,
      zIndex: 3,
      transition: 'none',
    }
  }
  const distance = slotDistance()
  if (originIndex.value < targetIndex.value && index > originIndex.value && index <= targetIndex.value)
    return { transform: `translate3d(0, ${-distance}px, 0)` }
  if (originIndex.value > targetIndex.value && index >= targetIndex.value && index < originIndex.value)
    return { transform: `translate3d(0, ${distance}px, 0)` }
  return {}
}

onBeforeUnmount(() => resetDrag())
watch(() => props.plans.map(plan => plan.id).join('\0'), () => resetDrag(Boolean(draggingId.value)))
watch(() => props.disabled, disabled => disabled && resetDrag(Boolean(draggingId.value)))
defineExpose({ cancelDrag: () => resetDrag(Boolean(draggingId.value)) })
</script>

<template>
  <view class="plan-sort-list" :class="{ 'plan-sort-list-dragging': draggingId }">
    <view
      v-for="(plan, index) in plans"
      :key="plan.id"
      class="plan-sort-item"
      :style="itemStyle(plan, index)"
      @touchstart="onTouchStart($event, plan, index)"
      @touchmove="onTouchMove"
      @touchend="onTouchEnd"
      @touchcancel="resetDrag(Boolean(draggingId))"
    >
      <FitnessPlanCard
        :plan="plan"
        :dragging="draggingId === plan.id"
        @select="selectPlan(plan)"
      />
    </view>
    <text v-if="disabled" class="plan-sort-status">正在保存顺序…</text>
  </view>
</template>

<style scoped lang="scss">
.plan-sort-list {
  position: relative;
  border-bottom: 1rpx solid #d5d3cc;
}

.plan-sort-list-dragging {
  touch-action: none;
}

.plan-sort-item {
  position: relative;
  transition: transform 180ms cubic-bezier(0.2, 0.75, 0.25, 1);
  will-change: transform;
}

.plan-sort-status {
  display: block;
  padding-top: 14rpx;
  color: #176b57;
  font-size: 19rpx;
  font-weight: 700;
  text-align: right;
}
</style>
