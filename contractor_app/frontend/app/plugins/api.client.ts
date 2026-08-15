import { createMockApiClient } from '~/services/api/mock/mockClient'
import { createHttpApiClient } from '~/services/api/httpClient'
import type { ApiClient } from '~/services/api/client'

export default defineNuxtPlugin(() => {
  const config = useRuntimeConfig()
  const mode = String(config.public.apiMode || 'mock')
  const baseUrl = String(config.public.apiBaseUrl || '')

  const api: ApiClient =
    mode === 'http' ? createHttpApiClient(baseUrl) : createMockApiClient()

  return {
    provide: {
      api,
    },
  }
})
