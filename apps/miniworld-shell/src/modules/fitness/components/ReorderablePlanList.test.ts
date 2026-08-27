import type { VueWrapper } from '@vue/test-utils'
import type { FitnessPlan } from '@/modules/fitness'
import { mount } from '@vue/test-utils'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import ReorderablePlanList from './ReorderablePlanList.vue'

const plans: FitnessPlan[] = ['胸', '背', '肩', '臀腿'].map((name, index) => ({
  id: `plan-${index + 1}`,
  name,
  sortOrder: index,
  exerciseCount: index,
  createdAt: '',
  updatedAt: '',
}))

function mountList(): VueWrapper {
  return mount(ReorderablePlanList, { props: { plans } })
}

function touch(clientY: number) {
  return { touches: [{ clientY }], changedTouches: [{ clientY }] }
}

beforeEach(() => {
  vi.useFakeTimers()
  const query = {
    in: vi.fn().mockReturnThis(),
    selectAll: vi.fn().mockReturnThis(),
    boundingClientRect: vi.fn((callback: (rects: object[]) => void) => {
      callback(plans.map((_, index) => ({ top: index * 100, height: 100 })))
      return query
    }),
    exec: vi.fn(),
  }
  Object.assign(uni, {
    createSelectorQuery: vi.fn(() => query),
    vibrateShort: vi.fn(),
  })
})

afterEach(() => vi.useRealTimers())

describe('reorderable fitness plan list', () => {
  it('selects a plan after a short tap', async () => {
    const wrapper = mountList()
    const first = wrapper.findAll('.plan-sort-item')[0]
    await first.trigger('touchstart', touch(50))
    await first.trigger('touchend', touch(50))
    await first.get('.plan-card').trigger('click')

    expect(wrapper.emitted('select')?.[0]?.[0]).toEqual(plans[0])
    expect(wrapper.emitted('reorder')).toBeUndefined()
  })

  it('treats movement before the long press as page scrolling', async () => {
    const wrapper = mountList()
    const first = wrapper.findAll('.plan-sort-item')[0]
    await first.trigger('touchstart', touch(50))
    await first.trigger('touchmove', touch(59))
    await vi.advanceTimersByTimeAsync(400)
    await first.trigger('touchend', touch(59))
    await first.get('.plan-card').trigger('click')

    expect(wrapper.emitted('select')).toBeUndefined()
    expect(wrapper.emitted('reorder')).toBeUndefined()
    expect(uni.vibrateShort).not.toHaveBeenCalled()
  })

  it('emits one reordered id list and suppresses the following click', async () => {
    const wrapper = mountList()
    const first = wrapper.findAll('.plan-sort-item')[0]
    await first.trigger('touchstart', touch(50))
    await vi.advanceTimersByTimeAsync(350)
    await first.trigger('touchmove', touch(220))
    await first.trigger('touchend', touch(220))
    await first.get('.plan-card').trigger('click')

    expect(uni.vibrateShort).toHaveBeenCalledTimes(1)
    expect(wrapper.emitted('reorder')).toEqual([[['plan-2', 'plan-1', 'plan-3', 'plan-4']]])
    expect(wrapper.emitted('select')).toBeUndefined()
  })

  it('changes slots only after the dragged card center crosses a neighbour midpoint', async () => {
    const wrapper = mountList()
    const first = wrapper.findAll('.plan-sort-item')[0]
    await first.trigger('touchstart', touch(10))
    await vi.advanceTimersByTimeAsync(350)
    await first.trigger('touchmove', touch(70))
    await first.trigger('touchend', touch(70))

    expect(wrapper.emitted('reorder')).toBeUndefined()
  })

  it('does not submit an unchanged or cancelled drag', async () => {
    const wrapper = mountList()
    const first = wrapper.findAll('.plan-sort-item')[0]
    await first.trigger('touchstart', touch(50))
    await vi.advanceTimersByTimeAsync(350)
    await first.trigger('touchend', touch(50))
    expect(wrapper.emitted('reorder')).toBeUndefined()

    await first.trigger('touchstart', touch(50))
    await vi.advanceTimersByTimeAsync(350)
    await first.trigger('touchmove', touch(220))
    await first.trigger('touchcancel', touch(220))
    expect(wrapper.emitted('reorder')).toBeUndefined()
    expect(wrapper.find('.plan-sort-list-dragging').exists()).toBe(false)
  })

  it('resets an active drag when plan data refreshes', async () => {
    const wrapper = mountList()
    const first = wrapper.findAll('.plan-sort-item')[0]
    await first.trigger('touchstart', touch(50))
    await vi.advanceTimersByTimeAsync(350)
    expect(wrapper.find('.plan-sort-list-dragging').exists()).toBe(true)

    await wrapper.setProps({ plans: [...plans].reverse() })

    expect(wrapper.find('.plan-sort-list-dragging').exists()).toBe(false)
    expect(wrapper.emitted('reorder')).toBeUndefined()
  })
})
