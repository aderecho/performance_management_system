import { defineStore, acceptHMRUpdate } from 'pinia'
import { api } from 'src/boot/axios'

export const useAuditLogStore = defineStore('auditLogStore', {
  state: () => ({
    logs: [],
    loading: {
      list: false,
    },
    error: {
      list: null,
    },
  }),

  actions: {
    async fetchAuditLogs(params = {}) {
      this.loading.list = true
      this.error.list = null

      const cleanedParams = Object.fromEntries(
        Object.entries(params).filter(([, value]) => value !== null && value !== undefined && value !== ''),
      )

      try {
        const response = await api.get('/auth/audit-logs/', { params: cleanedParams })
        this.logs = response.data
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
  import.meta.hot.accept(acceptHMRUpdate(useAuditLogStore, import.meta.hot))
}
