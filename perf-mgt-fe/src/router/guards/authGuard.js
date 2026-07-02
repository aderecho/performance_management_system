import { useAuthStore } from 'src/stores/auth'

export async function authGuard(to, from, next) {
  const auth = useAuthStore()
  const requiresAuth = to.matched.some((route) => route.meta.requiresAuth)

  // Check for existing session
  if (!auth.sessionChecked) {
    await auth.checkSession()
  }

  const homePath = auth.canAccess({ requiredPermission: 'pme.view_document' })
    ? '/admin/dashboard'
    : '/documents'

  // Require authentication if user is not logged in
  if (requiresAuth && !auth.isAuthenticated) {
    return next('/login')
  }

  if (requiresAuth && !auth.canAccess(to.meta)) {
    return next(to.path === homePath ? false : homePath)
  }

  // Redirect logged-in users away from /login
  if (to.path === '/login' && auth.isAuthenticated) {
    return next(homePath)
  }

  return next()
}
