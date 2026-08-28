<script setup lang="ts">
import * as echarts from 'echarts/dist/echarts.esm.js'
import { nextTick, onBeforeUnmount, ref, watch } from 'vue'
import type { EChartsOption } from 'echarts'
import type { ExerciseProgress, ProgressMode } from '../types'
import type { ProgressChartType } from './progressChart'
import { buildProgressOption } from './progressChart'
import LimeEchart from '@/uni_modules/lime-echart/components/l-echart/l-echart.vue'

const props = withDefaults(defineProps<{
  progress: ExerciseProgress | null
  mode?: ProgressMode
  chartType?: ProgressChartType
}>(), {
  mode: 'day',
  chartType: 'line',
})

const chartRef = ref<InstanceType<typeof LimeEchart> | null>(null)
const chart = ref<{ setOption: (option: EChartsOption, opts?: unknown) => void } | null>(null)
const ready = ref(false)

async function renderChart() {
  if (!ready.value || !chart.value)
    return
  await nextTick()
  chart.value.setOption(buildProgressOption(props.progress, props.mode, props.chartType), true)
}

async function onChartReady() {
  if (!chartRef.value)
    return
  const instance = await chartRef.value.init(echarts)
  if (!instance)
    return
  chart.value = instance
  ready.value = true
  await renderChart()
}

watch(() => [props.progress, props.mode, props.chartType], renderChart, { deep: true })
onBeforeUnmount(() => {
  ready.value = false
  chart.value = null
})
</script>

<template>
  <view class="progress-chart-shell">
    <view v-if="!progress?.points.length" class="chart-empty">
      完成至少一次包含该动作的训练后显示趋势。
    </view>
    <view v-else class="progress-chart-canvas">
      <LimeEchart ref="chartRef" custom-style="width:100%;height:100%;" @finished="onChartReady" />
    </view>
  </view>
</template>

<style scoped lang="scss">
.progress-chart-shell {
  width: 100%;
}

.progress-chart-canvas {
  width: 100%;
  height: 420rpx;
  min-height: 260px;
  overflow: hidden;
}

.chart-empty {
  display: block;
  padding: 42rpx 0;
  color: #777a73;
  font-size: 22rpx;
  line-height: 1.6;
}
</style>
