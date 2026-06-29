import { defineStore, acceptHMRUpdate } from 'pinia'
import { api } from 'src/boot/axios'

export const usePermissionStore = defineStore('permissionStore', {
  state: () => ({
    permissions: [],
    loading: {
      list: false,
    },
    error: {
      list: null,
    },
  }),

  getters: {
    options: (state) => state.permissions.map((permission) => ({
      label: permission.name,
      value: permission.id,
      ...permission,
    })),
  },

  actions: {
    async fetchPermissions() {
      this.loading.list = true
      this.error.list = null

      try {
        const response = await api.get('/auth/permissions/')
        this.permissions = response.data
        return response.data
      } catch (err) {
        this.error.list = err.response?.data || err.message
        throw err
      } finally {
        this.loading.list = false
      }
    },
  },
})

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(usePermissionStore, import.meta.hot))
}
