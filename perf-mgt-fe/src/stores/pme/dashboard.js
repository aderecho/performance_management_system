import { defineStore, acceptHMRUpdate } from 'pinia'
import { api } from 'boot/axios'
import { notify } from 'src/utils/notify'

export const useDashboardStore = defineStore('dashboardStore', {
  state: () => ({
    dashboardSummary: null,
    loading: false,
    error: null,
  }),

  actions: {
    async fetchDashboardSummary(params = {}) {
      this.loading = true
      this.error = null

      try {
        const response = await api.get('/pme/dashboard/summary/', { params })
        this.dashboardSummary = response.data
        return response.data
      } catch (err) {
        this.error = err.response?.data || err.message
        notify.negative(
          `Failed to load dashboard summary. ${err.response?.data?.message || 'Please try again.'}`,
        )
        throw err
      } finally {
        this.loading = false
      }
    },
  },
})

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useDashboardStore, import.meta.hot))
}
