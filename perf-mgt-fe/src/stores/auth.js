import { defineStore, acceptHMRUpdate } from 'pinia'
import { api } from 'src/boot/axios'

export const useAuthStore = defineStore('authStore', {
  state: () => ({
    checkingSession: false,
    user: null,
    roles: [],
    permissions: [],
    // initialized: false,
    sessionChecked: false,
  }),

  getters: {
    isAuthenticated: (state) => !!state.user,

    isSuperAdmin: (state) => state.user?.is_superadmin === true,

    hasRole: (state) => (role) =>
      state.roles.includes(role),

    hasPermission: (state) => (permission) =>
      state.permissions.includes(permission),

    hasAnyRole: (state) => (roles) =>
      roles.some((role) => state.roles.includes(role)),

    hasAllPermissions: (state) => (permissions) =>
      permissions.every((permission) => state.permissions.includes(permission)),

    canAccess: (state) => (meta = {}) => {
      if (!state.user) return false
      if (state.user?.is_superadmin === true) return true
      if (meta.requiresSuperAdmin) return false

      const normalize = (value) => {
        if (!value) return []
        return Array.isArray(value) ? value : [value]
      }

      const requiredRoles = normalize(meta.requiredRoles || meta.requiredRole)
      const requiredPermissions = normalize(meta.requiredPermissions || meta.requiredPermission)

      if (requiredRoles.length && !requiredRoles.some((role) => state.roles.includes(role))) {
        return false
      }

      if (
        requiredPermissions.length &&
        !requiredPermissions.every((permission) => state.permissions.includes(permission))
      ) {
        return false
      }

      return true
    },
  },

  actions: {
    clearSession() {
      this.user = null
      this.roles = []
      this.permissions = []
      this.sessionChecked = true
    },

    async login(email, password) {
      this.checkingSession = true

      try {
        await api.post('/auth/login/', { email, password })
        const user = await this.checkSession()

        if (!user) {
          throw new Error('Unable to verify session.')
        }

        return user
      } catch (err) {
        this.clearSession()
        throw err
      } finally {
        this.checkingSession = false
      }
    },

    async checkSession() {
      this.checkingSession = true
      try {
        const res = await api.get('/auth/session/')
        this.user = res.data.user
        this.roles = res.data.user.roles || []
        this.permissions = res.data.user.permissions || []
        this.sessionChecked = true
        return this.user
      } catch {
        this.clearSession()
        return null
      } finally {
        this.checkingSession = false
      }
    },

    async logout() {
      try {
        await api.post('/auth/logout/')
        return true
      } finally {
        this.clearSession()
      }
    }
  },
})

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useAuthStore, import.meta.hot))
}
