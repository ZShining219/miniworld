import { defineConfig } from 'openapi-ts-request'

export default defineConfig([
  {
    describe: 'MiniWorld local API',
    schemaPath: 'http://127.0.0.1:8000/openapi.json',
    serversPath: './src/service',
    requestLibPath: `import request from '@/http/vue-query';\n import { CustomRequestOptions_ } from '@/http/types';`,
    requestOptionsType: 'CustomRequestOptions_',
    isGenReactQuery: false,
    reactQueryMode: 'vue',
    isGenJavaScript: false,
  },
])
