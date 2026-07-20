export default defineNuxtRouteMiddleware(async (to) => {
  const auth = useAuth()
  if (!auth.hydrated.value) {
    auth.loadFromStorage()
  }

  const publicPaths = new Set(['/login', '/register'])
  const isPublic = publicPaths.has(to.path)

  if (!auth.isAuthenticated.value && !isPublic) {
    return navigateTo('/login')
  }

  if (auth.isAuthenticated.value && (to.path === '/login' || to.path === '/register')) {
    return navigateTo('/')
  }
})
