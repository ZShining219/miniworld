import type { EChartsOption } from 'echarts'
import type { ExerciseProgress, ProgressDayPoint, ProgressMode, ProgressSetPoint } from '../types'

export type ProgressChartType = 'line' | 'bar'

function shortDate(value: string) {
  return value.length >= 10 ? value.slice(5, 10) : value
}

function asSetPoints(progress: ExerciseProgress): ProgressSetPoint[] {
  return progress.mode === 'set' ? progress.points as ProgressSetPoint[] : []
}

function asDayPoints(progress: ExerciseProgress): ProgressDayPoint[] {
  return progress.mode === 'day' ? progress.points as ProgressDayPoint[] : []
}

export function buildProgressOption(
  progress: ExerciseProgress | null,
  mode: ProgressMode,
  chartType: ProgressChartType,
): EChartsOption {
  const points = progress?.mode === mode ? progress : null
  const setPoints = points ? asSetPoints(points) : []
  const dayPoints = points ? asDayPoints(points) : []
  const labels = mode === 'set'
    ? setPoints.map(point => `${shortDate(point.workoutDate)} #${point.setOrder}`)
    : dayPoints.map(point => shortDate(point.workoutDate))
  const values = mode === 'set'
    ? setPoints.map(point => point.weight)
    : dayPoints.map(point => point.averageWeight)
  const visiblePointCount = 12
  const start = labels.length > visiblePointCount
    ? Math.round(((labels.length - visiblePointCount) / labels.length) * 100)
    : 0

  const tooltipFormatter = (params: unknown) => {
    const item = Array.isArray(params) ? params[0] as { dataIndex?: number, value?: number } : params as { dataIndex?: number, value?: number }
    const index = item?.dataIndex ?? 0
    if (mode === 'set') {
      const point = setPoints[index]
      return point
        ? `${point.workoutDate}<br/>第 ${point.setOrder} 组 · ${point.weight} kg × ${point.reps}`
        : ''
    }
    const point = dayPoints[index]
    return point
      ? `${point.workoutDate}<br/>平均 ${point.averageWeight} kg<br/>范围 ${point.minWeight}–${point.maxWeight} kg · ${point.setCount} 组`
      : ''
  }

  return {
    animation: false,
    grid: { left: 42, right: 16, top: 24, bottom: 34, containLabel: true },
    tooltip: {
      trigger: 'axis',
      confine: true,
      formatter: tooltipFormatter,
    },
    dataZoom: [{
      type: 'inside',
      start,
      end: 100,
      zoomOnMouseWheel: true,
      moveOnMouseMove: true,
      moveOnMouseWheel: false,
    }],
    xAxis: {
      type: 'category',
      boundaryGap: chartType === 'bar',
      data: labels,
      axisLabel: { color: '#777a73', hideOverlap: true },
      axisLine: { lineStyle: { color: '#c9c8c1' } },
    },
    yAxis: {
      type: 'value',
      name: 'kg',
      nameTextStyle: { color: '#777a73' },
      axisLabel: { color: '#777a73' },
      splitLine: { lineStyle: { color: '#e0ded7' } },
    },
    series: [{
      type: chartType,
      name: mode === 'set' ? '每组重量' : '平均重量',
      data: values,
      ...(chartType === 'line'
        ? { smooth: false, symbol: 'circle', symbolSize: 7, lineStyle: { color: '#176b57', width: 3 }, itemStyle: { color: '#cf533d' } }
        : { barMaxWidth: 26, itemStyle: { color: '#176b57' } }),
    }],
  }
}
