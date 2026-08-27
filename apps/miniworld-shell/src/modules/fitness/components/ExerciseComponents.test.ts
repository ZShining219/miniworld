import type { FitnessExercise, FitnessPlan, WorkoutSet } from '@/modules/fitness'
import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import ExerciseDefaultsFields from './ExerciseDefaultsFields.vue'
import FitnessExerciseEditorRow from './FitnessExerciseEditorRow.vue'
import FitnessExerciseRow from './FitnessExerciseRow.vue'
import FitnessPlanEditorRow from './FitnessPlanEditorRow.vue'
import WorkoutSetList from './WorkoutSetList.vue'

const exercise: FitnessExercise = {
  id: 'exercise-1',
  planId: 'plan-1',
  name: '杠铃卧推',
  defaultWeight: 80,
  defaultReps: 8,
  sortOrder: 0,
  createdAt: '',
  updatedAt: '',
}

const plan: FitnessPlan = {
  id: 'plan-1',
  name: '胸',
  sortOrder: 0,
  exerciseCount: 1,
  createdAt: '',
  updatedAt: '',
}

const set: WorkoutSet = {
  id: 'set-1',
  sessionId: 'session-1',
  exerciseId: exercise.id,
  exerciseNameSnapshot: exercise.name,
  weight: 82.5,
  reps: 8,
  setOrder: 1,
  completedAt: '',
}

describe('fitness exercise components', () => {
  it('labels exercise defaults and emits normalized field values', async () => {
    const wrapper = mount(ExerciseDefaultsFields, {
      props: { name: exercise.name, weight: exercise.defaultWeight, reps: exercise.defaultReps },
    })
    const inputs = wrapper.findAll('input')

    expect(wrapper.text()).toContain('动作名称')
    expect(wrapper.text()).toContain('默认重量（kg）')
    expect(wrapper.text()).toContain('默认次数（次）')
    await inputs[0].trigger('input', { detail: { value: '上斜卧推' } })
    await inputs[1].trigger('input', { detail: { value: '82.5' } })
    await inputs[2].trigger('input', { detail: { value: '10' } })

    expect(wrapper.emitted('update:name')).toEqual([['上斜卧推']])
    expect(wrapper.emitted('update:weight')).toEqual([[82.5]])
    expect(wrapper.emitted('update:reps')).toEqual([[10]])
  })

  it('separates exercise selection from the trailing row action', async () => {
    const wrapper = mount(FitnessExerciseRow, {
      props: { exercise, meta: '建议 80 kg · 8 次', index: 0, actionLabel: '停用' },
    })

    await wrapper.get('.fitness-list-copy').trigger('click')
    expect(wrapper.emitted('select')).toHaveLength(1)
    await wrapper.get('.fitness-exercise-action').trigger('click')
    expect(wrapper.emitted('action')).toHaveLength(1)
    expect(wrapper.emitted('select')).toHaveLength(1)
  })

  it('formats saved sets consistently and can show the repetitions unit', () => {
    const wrapper = mount(WorkoutSetList, { props: { sets: [set], showRepsUnit: true } })
    expect(wrapper.get('.workout-set-order').text()).toBe('01')
    expect(wrapper.get('.workout-set-value').text()).toBe('82.5 kg × 8 次')
  })

  it('keeps plan editing labeled and emits explicit commands', async () => {
    const wrapper = mount(FitnessPlanEditorRow, { props: { plan, selected: true } })
    expect(wrapper.text()).toContain('计划名称')
    await wrapper.get('input').trigger('focus')
    await wrapper.get('input').trigger('input', { detail: { value: '上肢' } })
    await wrapper.get('.fitness-secondary').trigger('click')

    expect(wrapper.emitted('select')).toHaveLength(1)
    expect(wrapper.emitted('update:name')).toEqual([['上肢']])
    expect(wrapper.emitted('save')).toHaveLength(1)
  })

  it('keeps exercise editor movement at the presentation boundary', async () => {
    const wrapper = mount(FitnessExerciseEditorRow, {
      props: { exercise, first: false, last: true },
    })
    const moveButtons = wrapper.findAll('.fitness-icon-button')
    expect(moveButtons[0].attributes('disabled')).toBeUndefined()
    expect(moveButtons[1].attributes('disabled')).toBeDefined()
    await moveButtons[0].trigger('click')
    expect(wrapper.emitted('move')).toEqual([[-1]])
  })
})
