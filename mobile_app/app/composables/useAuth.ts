/**
 * Auth state for the contractor mobile app.
 * Tokens live in localStorage for MVP (Bearer to API).
 */

export type AuthUser = {
  id: string
  email: string
  full_name: string
  phone?: string | null
}

export type AuthCompany = {
  id: string
  name: string
  slug: string
  trade?: string | null
  onboarding_completed: boolean
}

export type AuthMembership = {
  id: string
  company_id: string
  role: string
  status: string
}

export type AuthPermissions = {
  can_manage_team: boolean
  can_approve_and_publish: boolean
  can_create_jobs: boolean
  role: string | null
}

const ACCESS_KEY = 'jp_access_token'
const REFRESH_KEY = 'jp_refresh_token'

export const useAuth = () => {
  const accessToken = useState<string | null>('auth.accessToken', () => null)
  const refreshToken = useState<string | null>('auth.refreshToken', () => null)
  const user = useState<AuthUser | null>('auth.user', () => null)
  const company = useState<AuthCompany | null>('auth.company', () => null)
  const membership = useState<AuthMembership | null>('auth.membership', () => null)
  const permissions = useState<AuthPermissions | null>('auth.permissions', () => null)
  const hydrated = useState<boolean>('auth.hydrated', () => false)

  const isAuthenticated = computed(() => Boolean(accessToken.value))

  function loadFromStorage() {
    if (!import.meta.client) return
    accessToken.value = localStorage.getItem(ACCESS_KEY)
    refreshToken.value = localStorage.getItem(REFRESH_KEY)
    hydrated.value = true
  }

  function persistTokens(access: string, refresh: string) {
    accessToken.value = access
    refreshToken.value = refresh
    if (import.meta.client) {
      localStorage.setItem(ACCESS_KEY, access)
      localStorage.setItem(REFRESH_KEY, refresh)
    }
  }

  function setSession(payload: {
    access_token: string
    refresh_token: string
    user: AuthUser
    company?: AuthCompany | null
    membership?: AuthMembership | null
    permissions?: AuthPermissions | null
  }) {
    persistTokens(payload.access_token, payload.refresh_token)
    user.value = payload.user
    company.value = payload.company ?? null
    membership.value = payload.membership ?? null
    if (payload.permissions) {
      permissions.value = payload.permissions
    }
  }

  function clearSession() {
    accessToken.value = null
    refreshToken.value = null
    user.value = null
    company.value = null
    membership.value = null
    permissions.value = null
    if (import.meta.client) {
      localStorage.removeItem(ACCESS_KEY)
      localStorage.removeItem(REFRESH_KEY)
    }
  }

  async function logout() {
    const config = useRuntimeConfig()
    try {
      if (accessToken.value) {
        await fetch(`${config.public.apiBase}/api/v1/auth/logout`, {
          method: 'POST',
          headers: { Authorization: `Bearer ${accessToken.value}` },
        })
      }
    } catch {
      // ignore network errors on logout
    }
    clearSession()
    await navigateTo('/login')
  }

  return {
    accessToken,
    refreshToken,
    user,
    company,
    membership,
    permissions,
    hydrated,
    isAuthenticated,
    loadFromStorage,
    setSession,
    clearSession,
    logout,
  }
}
