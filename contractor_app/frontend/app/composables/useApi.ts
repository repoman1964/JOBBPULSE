import type { ApiClient } from '~/services/api/client'

export function useApi(): ApiClient {
  const { $api } = useNuxtApp()
  return $api as ApiClient
}
