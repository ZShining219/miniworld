import type { SessionExerciseSummary } from '@/modules/fitness'
import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import FitnessExerciseSwitcher from './FitnessExerciseSwitcher.vue'

const exercises: SessionExerciseSummary[] = [
  {
    exercise: {
      id: 'bench',
      planId: 'chest',
      name: '杠铃卧推',
      defaultWeight: 80,
      defaultReps: 8,
      weightStep: 2.5,
      sortOrder: 0,
      createdAt: '',
      updatedAt: '',
    },
    completedSetCount: 3,
  },
  {
    exercise: {
      id: 'incline',
      planId: 'chest',
      name: '上斜哑铃卧推',
      defaultWeight: 25,
      defaultReps: 10,
      weightStep: 1,
      sortOrder: 1,
      createdAt: '',
      updatedAt: '',
    },
    completedSetCount: 1,
  },
]

describe('fitness exercise switcher', () => {
  it('shows ordered set counts and only emits another exercise', async () => {
    const wrapper = mount(FitnessExerciseSwitcher, {
      props: { exercises, currentId: 'bench' },
      global: { stubs: { 'scroll-view': { template: '<div><slot /></div>' } } },
    })
    const buttons = wrapper.findAll('.exercise-switcher-item')
    expect(buttons.map(button => button.text())).toEqual([
      '杠铃卧推今日 3 组',
      '上斜哑铃卧推今日 1 组',
    ])
    expect(buttons[0].attributes('aria-current')).toBe('page')
    await buttons[0].trigger('click')
    expect(wrapper.emitted('select')).toBeUndefined()
    await buttons[1].trigger('click')
    expect(wrapper.emitted('select')).toEqual([['incline']])
  })

  it('blocks switching while a set or step is saving', async () => {
    const wrapper = mount(FitnessExerciseSwitcher, {
      props: { exercises, currentId: 'bench', disabled: true },
      global: { stubs: { 'scroll-view': { template: '<div><slot /></div>' } } },
    })
    await wrapper.findAll('.exercise-switcher-item')[1].trigger('click')
    expect(wrapper.emitted('select')).toBeUndefined()
  })
})
