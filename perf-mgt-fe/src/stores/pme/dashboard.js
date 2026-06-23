import { defineStore, acceptHMRUpdate } from 'pinia'
import { api } from 'boot/axios'

let fetchDashboardSummaryRequestKey = 0

export const useDashboardStore = defineStore('dashboardStore', {
  state: () => ({
    dashboardSummary: null,
    loading: false,
    error: null,
  }),

  actions: {
    async fetchDashboardSummary(params = {}) {
      const requestKey = ++fetchDashboardSummaryRequestKey
      this.loading = true
      this.error = null

      try {
        const response = await api.get('/pme/dashboard/summary/', { params })

        if (requestKey !== fetchDashboardSummaryRequestKey) {
          return response.data
        }

        this.dashboardSummary = response.data
        return response.data
      } catch (err) {
        if (requestKey !== fetchDashboardSummaryRequestKey) {
          return null
        }

        this.error = err.response?.data || err.message
        throw err
      } finally {
        if (requestKey === fetchDashboardSummaryRequestKey) {
          this.loading = false
        }
      }
    },
  },
})

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useDashboardStore, import.meta.hot))
}
