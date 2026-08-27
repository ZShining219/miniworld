import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import FitnessChoiceChips from './FitnessChoiceChips.vue'
import FitnessPageShell from './FitnessPageShell.vue'
import FitnessSectionHeader from './FitnessSectionHeader.vue'

describe('fitness presentation primitives', () => {
  it('renders a consistent page heading, error and page content', () => {
    const wrapper = mount(FitnessPageShell, {
      props: {
        eyebrow: 'FITNESS HISTORY',
        title: '训练历史',
        subtitle: '这里只统计已经结束的训练。',
        error: '暂时无法读取训练历史。',
      },
      slots: { default: '<view class="page-content">内容</view>' },
    })

    expect(wrapper.get('.fitness-eyebrow').text()).toBe('FITNESS HISTORY')
    expect(wrapper.get('.fitness-title').text()).toBe('训练历史')
    expect(wrapper.get('[role="alert"]').text()).toBe('暂时无法读取训练历史。')
    expect(wrapper.get('.page-content').text()).toBe('内容')
  })

  it('keeps section copy and trailing controls in one header contract', () => {
    const wrapper = mount(FitnessSectionHeader, {
      props: { title: '本次动作', subtitle: '选择任意动作继续' },
      slots: { right: '<button class="manage">管理</button>' },
    })

    expect(wrapper.get('.fitness-section-title').text()).toBe('本次动作')
    expect(wrapper.get('.fitness-meta').text()).toBe('选择任意动作继续')
    expect(wrapper.get('.manage').text()).toBe('管理')
  })

  it('emits the selected chip id and exposes its pressed state', async () => {
    const wrapper = mount(FitnessChoiceChips, {
      props: {
        items: [{ id: 'chest', name: '胸' }, { id: 'back', name: '背' }],
        modelValue: 'chest',
        label: '选择训练部位',
      },
    })

    const buttons = wrapper.findAll('button')
    expect(buttons[0].attributes('aria-pressed')).toBe('true')
    await buttons[1].trigger('click')
    expect(wrapper.emitted('select')).toEqual([['back']])
  })
})
