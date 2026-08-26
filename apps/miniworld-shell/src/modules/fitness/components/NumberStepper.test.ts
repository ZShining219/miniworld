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
})
