export default defineNuxtPlugin(async () => {
  const auth = useAuth()
  const api = useApi()

  auth.loadFromStorage()

  if (!auth.accessToken.value) return

  try {
    const me = (await api.me()) as {
      user: any
      company: any
      membership: any
      permissions: any
    }
    auth.user.value = me.user
    auth.company.value = me.company
    auth.membership.value = me.membership
    auth.permissions.value = me.permissions
  } catch {
    auth.clearSession()
  }
})
