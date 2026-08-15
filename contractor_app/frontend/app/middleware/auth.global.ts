export default defineNuxtRouteMiddleware(async (to) => {
  if (import.meta.server) return

  const publicPaths = ['/sign-in']
  const { session, ready, refresh } = useAuthSession()

  if (!ready.value) {
    await refresh()
  }

  const isPublic = publicPaths.includes(to.path)

  if (!session.value && !isPublic) {
    return navigateTo({
      path: '/sign-in',
      query: { redirect: to.fullPath },
    })
  }

  if (session.value && to.path === '/sign-in') {
    return navigateTo('/jobs')
  }
})
