/**
 * In-app notifications (Phase 8 pilot hardening).
 */

export type AppNotification = {
  id: string
  user_id: string
  company_id: string
  type: string
  title: string
  body: string
  channel: string
  status: string
  read_at?: string | null
  sent_at?: string | null
  metadata_json?: Record<string, unknown> | null
  created_at?: string
}

type NotificationList = {
  items: AppNotification[]
  unread_count: number
  limit: number
  offset: number
}

export const useNotifications = () => {
  const api = useApi()
  const busy = ref(false)
  const error = ref<string | null>(null)
  const items = ref<AppNotification[]>([])
  const unreadCount = ref(0)

  async function list(opts?: { unreadOnly?: boolean }): Promise<NotificationList> {
    busy.value = true
    error.value = null
    try {
      const q = opts?.unreadOnly ? '?unread_only=true' : ''
      const data = await api.request<NotificationList>(`/api/v1/notifications${q}`)
      items.value = data.items || []
      unreadCount.value = data.unread_count ?? 0
      return data
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Could not load notifications'
      throw e
    } finally {
      busy.value = false
    }
  }

  async function markRead(id: string): Promise<AppNotification> {
    const n = await api.request<AppNotification>(`/api/v1/notifications/${id}/read`, {
      method: 'POST',
    })
    items.value = items.value.map((i) => (i.id === id ? n : i))
    unreadCount.value = Math.max(0, unreadCount.value - 1)
    return n
  }

  async function markAllRead(): Promise<void> {
    await api.request('/api/v1/notifications/read-all', { method: 'POST' })
    items.value = items.value.map((i) => ({ ...i, status: 'read' }))
    unreadCount.value = 0
  }

  function jobIdFrom(n: AppNotification): string | null {
    const meta = n.metadata_json
    if (!meta) return null
    const jid = meta.job_id
    return typeof jid === 'string' ? jid : null
  }

  return {
    busy,
    error,
    items,
    unreadCount,
    list,
    markRead,
    markAllRead,
    jobIdFrom,
  }
}
