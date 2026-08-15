import type { Session } from '~/types/domain'

const sessionState = () =>
  useState<Session | null>('auth-session', () => null)

const readyState = () => useState<boolean>('auth-ready', () => false)

export function useAuthSession() {
  const session = sessionState()
  const ready = readyState()
  const api = useApi()

  async function refresh() {
    try {
      session.value = await api.getSession()
    } catch {
      session.value = null
    } finally {
      ready.value = true
    }
  }

  async function setSession(next: Session | null) {
    session.value = next
    ready.value = true
  }

  async function logout() {
    await api.logout()
    session.value = null
  }

  return {
    session,
    ready,
    refresh,
    setSession,
    logout,
    isAuthenticated: computed(() => !!session.value),
  }
}
