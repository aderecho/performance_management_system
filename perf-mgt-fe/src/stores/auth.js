import { defineStore, acceptHMRUpdate } from 'pinia'
import { api } from 'src/boot/axios'
import { notify } from 'src/utils/notify'

export const useAuthStore = defineStore('authStore', {
  state: () => ({
    checkingSession: false,
    user: null,
    roles: [],
    permissions: [],
    initialized: false,
    sessionChecked: false,
  }),

  getters: {
    isAuthenticated: (state) => !!state.user,

    isSuperAdmin: (state) => state.user?.is_superadmin === true,

    hasRole: (state) => (role) =>
      state.roles.includes(role),

    hasPermission: (state) => (permission) =>
      state.permissions.includes(permission),
  },

  actions: {
    async login(email, password) {
      this.checkingSession = true

      try {
        await api.post('/auth/login/', { email, password })
        await this.checkSession()
        notify.positive(`Welcome back, ${email}!`)

        if (this.router.currentRoute.value.path === '/login') {
          this.router.push('/')
        }

      } catch {
        this.user = null
      } finally {
        this.checkingSession = false
      }
    },

    async checkSession() {
      this.checkingSession = true
      try {
        const res = await api.get('/auth/session')
        this.user = res.data.user
        this.roles = res.data.user.roles || []
        this.permissions = res.data.user.permissions || []
      } catch {
        this.user = null
        this.roles = []
        this.permissions = []
      } finally {
        this.checkingSession = false
      }
    },

    async logout() {
      await api.post('auth/logout/')
      this.user = null
      this.roles = []
      this.permissions = []
      this.router.push('/login')
    }
  },
})

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useAuthStore, import.meta.hot))
}
