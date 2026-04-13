import { useAuthStore } from 'src/stores/auth'

export async function authGuard(to, from, next) {
  const auth = useAuthStore()

  // Check for existing session
  if (!auth.sessionChecked) {
    auth.sessionChecked = true
    await auth.checkSession()
  }

  // Require authentication if user is not logged in
  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return next('/login')
  }

  // Redirect logged-in users away from /login
  if (to.path === '/login' && auth.isAuthenticated) {
    return next('/')
  }

  return next()
}