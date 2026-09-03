import type { ComponentResolver } from '@uni-helper/vite-plugin-uni-components'
import { kebabCase } from '@uni-helper/vite-plugin-uni-components'

/** Resolve Wot UI 2 npm components and their component-scoped styles. */
export function WotResolver(): ComponentResolver {
  return {
    type: 'component',
    resolve: (name: string) => {
      if (name.match(/^Wd[A-Z]/)) {
        const componentName = kebabCase(name)
        return {
          name,
          from: `@wot-ui/ui/components/${componentName}/${componentName}.vue`,
        }
      }
      if (name.startsWith('wd-')) {
        return {
          name,
          from: `@wot-ui/ui/components/${name}/${name}.vue`,
        }
      }
    },
  }
}
