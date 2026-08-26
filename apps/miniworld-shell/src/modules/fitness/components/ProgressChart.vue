<script setup lang="ts">
import type { ProgressPoint } from '../types'
import { getCurrentInstance, nextTick, watch } from 'vue'

const props = defineProps<{ points: ProgressPoint[] }>()
const instance = getCurrentInstance()

function draw() {
  const context = uni.createCanvasContext('fitness-progress-chart', instance?.proxy)
  const width = 320
  const height = 140
  context.clearRect(0, 0, width, height)
  context.setStrokeStyle('#c9c8c1')
  context.setLineWidth(1)
  context.beginPath()
  context.moveTo(20, 10)
  context.lineTo(20, 120)
  context.lineTo(305, 120)
  context.stroke()
  if (!props.points.length) {
    context.draw()
    return
  }
  const values = props.points.map(point => point.maxWeight)
  const min = Math.min(...values)
  const max = Math.max(...values)
  const range = Math.max(1, max - min)
  const coordinates = props.points.map((point, index) => ({
    x: props.points.length === 1 ? 160 : 26 + (index / (props.points.length - 1)) * 272,
    y: 112 - ((point.maxWeight - min) / range) * 88,
  }))
  context.setStrokeStyle('#176b57')
  context.setLineWidth(3)
  context.beginPath()
  coordinates.forEach((point, index) => index === 0 ? context.moveTo(point.x, point.y) : context.lineTo(point.x, point.y))
  context.stroke()
  context.setFillStyle('#cf533d')
  coordinates.forEach((point) => {
    context.beginPath()
    context.arc(point.x, point.y, 4, 0, Math.PI * 2)
    context.fill()
  })
  context.draw()
}

watch(() => props.points, () => nextTick(draw), { deep: true, immediate: true })
</script>

<template>
  <view class="chart-wrap">
    <canvas id="fitness-progress-chart" canvas-id="fitness-progress-chart" class="chart" />
    <view v-if="points.length" class="chart-labels">
      <text>{{ points[0].workoutDate.slice(5) }}</text>
      <text>{{ points[points.length - 1].workoutDate.slice(5) }}</text>
    </view>
    <text v-else class="chart-empty">完成至少一次包含该动作的训练后显示趋势。</text>
  </view>
</template>

<style scoped lang="scss">
.chart-wrap {
  width: 100%;
}

.chart {
  width: 640rpx;
  max-width: 100%;
  height: 280rpx;
}

.chart-labels {
  display: flex;
  justify-content: space-between;
  padding: 0 22rpx;
  color: #777a73;
  font-size: 19rpx;
}

.chart-empty {
  display: block;
  padding: 36rpx 0;
  color: #777a73;
  font-size: 22rpx;
}
</style>
