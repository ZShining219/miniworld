import { createPinia, setActivePinia } from 'pinia'
import { config } from '@vue/test-utils'
import { defineComponent, h } from 'vue'
import { beforeEach, vi } from 'vitest'

const WdButtonStub = defineComponent({
  name: 'WdButton',
  inheritAttrs: false,
  props: {
    disabled: Boolean,
    loading: Boolean,
  },
  emits: ['click'],
  setup(props, { attrs, emit, slots }) {
    return () => h('button', {
      ...attrs,
      disabled: props.disabled || props.loading || undefined,
      onClick: (event: Event) => emit('click', event),
    }, slots.default?.())
  },
})

const WdInputStub = defineComponent({
  name: 'WdInput',
  inheritAttrs: false,
  props: {
    modelValue: { type: [String, Number], default: '' },
    disabled: Boolean,
    focus: Boolean,
    type: { type: String, default: 'text' },
    placeholder: { type: String, default: '' },
  },
  emits: ['update:modelValue', 'input', 'focus', 'blur', 'confirm'],
  setup(props, { attrs, emit }) {
    function eventValue(event: Event) {
      const detail = (event as Event & { detail?: { value?: string } }).detail
      return detail?.value ?? (event.target as HTMLInputElement | null)?.value ?? ''
    }
    return () => h('input', {
      ...attrs,
      value: props.modelValue,
      disabled: props.disabled || undefined,
      autofocus: props.focus || undefined,
      type: props.type === 'digit' ? 'text' : props.type,
      placeholder: props.placeholder,
      onInput: (event: Event) => {
        const value = eventValue(event)
        emit('update:modelValue', value)
        emit('input', { value })
      },
      onFocus: (event: FocusEvent) => emit('focus', event),
      onBlur: (event: FocusEvent) => emit('blur', event),
      onKeyup: (event: KeyboardEvent) => event.key === 'Enter' && emit('confirm', event),
    })
  },
})

const WdEmptyStub = defineComponent({
  name: 'WdEmpty',
  props: { tip: { type: String, default: '' } },
  setup(props, { slots }) {
    return () => h('div', { class: 'wd-empty-stub' }, [props.tip, slots.default?.()])
  },
})

const WdLoadingStub = defineComponent({
  name: 'WdLoading',
  setup() {
    return () => h('span', { class: 'wd-loading-stub' }, '加载中')
  },
})

config.global.components = {
  WdButton: WdButtonStub,
  WdEmpty: WdEmptyStub,
  WdInput: WdInputStub,
  WdLoading: WdLoadingStub,
}

// 每个测试前重置 Pinia 实例，避免状态在测试间泄漏
beforeEach(() => {
  // 不注册 pinia-plugin-persistedstate，测试只验证 store 逻辑，不验证持久化行为
  setActivePinia(createPinia())
  // 重置所有 mock 的调用记录（保留实现，仅清空 .mock.calls 等）
  vi.clearAllMocks()
})

// 全局 mock uni 对象（jsdom 中无此全局，uni-app 特有）
const uniMock = {
  showToast: vi.fn(),
  hideToast: vi.fn(),
  showLoading: vi.fn(),
  hideLoading: vi.fn(),
  showModal: vi.fn(),
  navigateTo: vi.fn(),
  redirectTo: vi.fn(),
  navigateBack: vi.fn(),
  switchTab: vi.fn(),
  reLaunch: vi.fn(),
  // tabbar/store.ts 在模块初始化时调用 getStorageSync，返回 null 确保不影响初始状态
  getStorageSync: vi.fn().mockReturnValue(null),
  setStorageSync: vi.fn(),
  removeStorageSync: vi.fn(),
  getStorage: vi.fn(),
  setStorage: vi.fn(),
  removeStorage: vi.fn(),
  request: vi.fn(),
  uploadFile: vi.fn(),
  chooseImage: vi.fn(),
  getSystemInfoSync: vi.fn().mockReturnValue({ platform: 'devtools' }),
  getSystemInfo: vi.fn(),
  onNetworkStatusChange: vi.fn(),
  getNetworkType: vi.fn(),
}

Object.defineProperty(globalThis, 'uni', {
  value: uniMock,
  writable: true,
  configurable: true,
})

// getCurrentPages 是 uni-app 的全局函数（不在 uni 对象上）
Object.defineProperty(globalThis, 'getCurrentPages', {
  value: vi.fn().mockReturnValue([{ route: '/pages/index/index' }]),
  writable: true,
  configurable: true,
})
