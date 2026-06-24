import { useAuthStore } from 'src/stores/auth'

export async function authGuard(to, from, next) {
  const auth = useAuthStore()

  // Check for existing session
  if (!auth.sessionChecked) {
    await auth.checkSession()
  }

  // Require authentication if user is not logged in
  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return next('/login')
  }

  if (to.meta.requiresAuth && !auth.canAccess(to.meta)) {
    return next('/admin/dashboard')
  }

  // Redirect logged-in users away from /login
  if (to.path === '/login' && auth.isAuthenticated) {
    return next('/admin/dashboard')
  }

  return next()
}
