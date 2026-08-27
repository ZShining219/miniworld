import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import NumberStepper from './NumberStepper.vue'

describe('number stepper', () => {
  it('preserves decimal weight steps', async () => {
    const wrapper = mount(NumberStepper, {
      props: { modelValue: 80, label: '重量', step: 2.5 },
    })
    await wrapper.get('[aria-label="减少重量"]').trigger('click')
    expect(wrapper.emitted('update:modelValue')?.[0]).toEqual([77.5])
  })

  it.each([1, 2, 2.5, 5])('applies the selected %s kg step without floating drift', async (step) => {
    const wrapper = mount(NumberStepper, {
      props: { modelValue: 80, label: '重量', step, stepOptions: [1, 2, 2.5, 5] },
    })
    await wrapper.get('[aria-label="增加重量"]').trigger('click')
    expect(wrapper.emitted('update:modelValue')?.[0]).toEqual([80 + step])
  })

  it('emits a weight step selection without changing the value', async () => {
    const wrapper = mount(NumberStepper, {
      props: { modelValue: 80, label: '重量', step: 2.5, stepOptions: [1, 2, 2.5, 5] },
    })
    await wrapper.get('[aria-label="重量每次增减5"]').trigger('click')
    expect(wrapper.emitted('update:step')).toEqual([[5]])
    expect(wrapper.emitted('update:modelValue')).toBeUndefined()
  })

  it('accepts a two-decimal manual weight and rejects invalid input', async () => {
    const wrapper = mount(NumberStepper, {
      props: { modelValue: 80, label: '重量', editable: true, min: 0, max: 9999 },
    })
    await wrapper.get('[aria-label="手动输入重量"]').trigger('click')
    await wrapper.get('[aria-label="输入重量"]').trigger('input', { detail: { value: '82.25' } })
    await wrapper.get('[aria-label="输入重量"]').trigger('blur')
    expect(wrapper.emitted('update:modelValue')?.[0]).toEqual([82.25])

    await wrapper.get('[aria-label="手动输入重量"]').trigger('click')
    await wrapper.get('[aria-label="输入重量"]').trigger('input', { detail: { value: '82.255' } })
    await wrapper.get('[aria-label="输入重量"]').trigger('blur')
    expect(wrapper.emitted('update:modelValue')).toHaveLength(1)

    await wrapper.get('[aria-label="手动输入重量"]').trigger('click')
    await wrapper.get('[aria-label="输入重量"]').trigger('input', { detail: { value: '-1' } })
    await wrapper.get('[aria-label="输入重量"]').trigger('blur')
    expect(wrapper.emitted('update:modelValue')).toHaveLength(1)
  })

  it('keeps reps non-editable and clamps the minimum', async () => {
    const wrapper = mount(NumberStepper, {
      props: { modelValue: 0, label: '次数', min: 0, step: 1 },
    })
    expect(wrapper.find('[aria-label="手动输入次数"]').exists()).toBe(false)
    await wrapper.get('[aria-label="减少次数"]').trigger('click')
    expect(wrapper.emitted('update:modelValue')?.[0]).toEqual([0])
  })
})
