export interface MiniWorldModule {
  key: string
  title: string
  caption: string
  path: string
  state: string
  navigation: 'tab' | 'page'
}

export const moduleRegistry: MiniWorldModule[] = [
  { key: '01', title: '岗位发现', caption: 'Jobs', path: '/pages/jobs/jobs', state: '待接入', navigation: 'tab' },
  { key: '02', title: '个人档案', caption: 'Profile', path: '/pages/profile/profile', state: '待接入', navigation: 'tab' },
  { key: '03', title: '工作沉淀', caption: 'Work', path: '/pages/work/work', state: '待接入', navigation: 'tab' },
  { key: '04', title: '健身记录', caption: 'Fitness', path: '/pages/fitness/index', state: '可使用', navigation: 'page' },
]
