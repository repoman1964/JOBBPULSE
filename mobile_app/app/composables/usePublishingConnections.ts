/**
 * Social account connections (Phase 7 mock provider).
 */

export type PublishingConnection = {
  id: string
  company_id: string
  provider: string
  platform: string
  external_account_id?: string | null
  display_name: string
  status: string
  last_verified_at?: string | null
  last_error?: string | null
  created_at?: string
  updated_at?: string
}

export const usePublishingConnections = () => {
  const api = useApi()
  const busy = ref(false)
  const error = ref<string | null>(null)
  const connections = ref<PublishingConnection[]>([])

  async function list(): Promise<PublishingConnection[]> {
    busy.value = true
    error.value = null
    try {
      const data = await api.request<{ items: PublishingConnection[] }>(
        '/api/v1/publishing/connections',
      )
      connections.value = data.items || []
      return connections.value
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Could not load connections'
      throw e
    } finally {
      busy.value = false
    }
  }

  async function start(platform: string, displayName?: string): Promise<PublishingConnection> {
    busy.value = true
    error.value = null
    try {
      const conn = await api.request<PublishingConnection>(
        '/api/v1/publishing/connections/start',
        {
          method: 'POST',
          body: JSON.stringify({
            platform,
            display_name: displayName || undefined,
          }),
        },
      )
      await list()
      return conn
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Could not connect account'
      throw e
    } finally {
      busy.value = false
    }
  }

  async function disconnect(id: string): Promise<void> {
    busy.value = true
    error.value = null
    try {
      await api.request(`/api/v1/publishing/connections/${id}`, { method: 'DELETE' })
      await list()
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Could not disconnect'
      throw e
    } finally {
      busy.value = false
    }
  }

  const active = computed(() =>
    connections.value.filter((c) => c.status === 'active'),
  )

  return {
    busy,
    error,
    connections,
    active,
    list,
    start,
    disconnect,
  }
}
