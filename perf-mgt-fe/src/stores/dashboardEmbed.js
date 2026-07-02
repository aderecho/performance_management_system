import { defineStore, acceptHMRUpdate } from 'pinia'
import { api } from 'src/boot/axios'

export const useDashboardEmbedStore = defineStore('dashboardEmbedStore', {
  state: () => ({
    dashboards: [],
    loading: {
      list: false,
      save: false,
      delete: false,
    },
    error: {
      list: null,
      save: null,
      delete: null,
    },
  }),

  getters: {
    dashboardBySlug: (state) => (slug) =>
      state.dashboards.find((dashboard) => dashboard.slug === slug) || null,
  },

  actions: {
    async fetchDashboards() {
      this.loading.list = true
      this.error.list = null

      try {
        const response = await api.get('/pme/dashboard-embeds/')
        this.dashboards = response.data
        return response.data
      } catch (err) {
        this.error.list = err.response?.data || err.message
        throw err
      } finally {
        this.loading.list = false
      }
    },

    async createDashboard(payload) {
      this.loading.save = true
      this.error.save = null

      try {
        const response = await api.post('/pme/dashboard-embeds/', payload)
        this.dashboards = [...this.dashboards, response.data].sort((a, b) =>
          a.name.localeCompare(b.name),
        )
        return response.data
      } catch (err) {
        this.error.save = err.response?.data || err.message
        throw err
      } finally {
        this.loading.save = false
      }
    },

    async updateDashboard(id, payload) {
      this.loading.save = true
      this.error.save = null

      try {
        const response = await api.patch(`/pme/dashboard-embeds/${id}/`, payload)
        const dashboardIndex = this.dashboards.findIndex((dashboard) => dashboard.id === id)

        if (dashboardIndex === -1) {
          this.dashboards = [...this.dashboards, response.data]
        } else {
          this.dashboards.splice(dashboardIndex, 1, response.data)
        }

        this.dashboards = [...this.dashboards].sort((a, b) => a.name.localeCompare(b.name))
        return response.data
      } catch (err) {
        this.error.save = err.response?.data || err.message
        throw err
      } finally {
        this.loading.save = false
      }
    },

    async deleteDashboard(id) {
      this.loading.delete = true
      this.error.delete = null

      try {
        await api.delete(`/pme/dashboard-embeds/${id}/`)
        this.dashboards = this.dashboards.filter((dashboard) => dashboard.id !== id)
      } catch (err) {
        this.error.delete = err.response?.data || err.message
        throw err
      } finally {
        this.loading.delete = false
      }
    },
  },
})

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useDashboardEmbedStore, import.meta.hot))
}
