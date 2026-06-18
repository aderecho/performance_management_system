import { defineStore, acceptHMRUpdate } from 'pinia'
import { api } from 'boot/axios'
import { notify } from 'src/utils/notify'

export const useInitiativeStore = defineStore('initiativeStore', {
  state: () => ({
    initiatives: [],
    loading: {
      list: false,
      save: false,
      delete: false,
      accomplishment: false,
    },
    error: {
      list: null,
      save: null,
      delete: null,
      accomplishment: null,
    }
  }),

  actions: {
    async fetchInitiatives(indicatorId, params = {}) {
      this.loading.list = true
      this.error.list = null

      try {
        const response = await api.get(`/pme/items/${indicatorId}/initiatives/`, { params })
        this.initiatives = response.data
        return response.data
      } catch (err) {
        this.error.list = err.response?.data || err.message
        this.initiatives = []
        notify.negative(
          `Failed to load initiatives. ${err.response?.data?.message || 'Please try again.'}`,
        )
        throw err
      } finally {
        this.loading.list = false
      }
    },

    async createInitiative(payload) {
      this.loading.save = true
      this.error.save = null

      try {
        const response = await api.post('/pme/initiatives/', payload)
        notify.positive('Initiative submitted successfully.')
        return response.data
      } catch (err) {
        this.error.save = err.response?.data || err.message
        notify.negative(`Failed to submit initiative. ${err.response?.data || 'Please try again.'}`)
        throw err
      } finally {
        this.loading.save = false
      }
    },

    async updateInitiative(id, payload) {
      this.loading.save = true
      this.error.save = null

      try {
        const response = await api.put(`/pme/initiatives/${id}/`, payload)
        notify.positive('Initiative updated successfully.')
        return response.data
      } catch (err) {
        this.error.save = err.response?.data || err.message
        notify.negative(`Failed to update initiative. ${err.response?.data || 'Please try again.'}`)
        throw err
      } finally {
        this.loading.save = false
      }
    },

    async deleteInitiative(id) {
      this.loading.delete = true
      this.error.delete = null

      try {
        await api.delete(`/pme/initiatives/${id}/`)
        this.initiatives = this.initiatives.filter((initiative) => initiative.id !== id)
        notify.positive('Initiative removed successfully.')
        return true
      } catch (err) {
        this.error.delete = err.response?.data || err.message
        notify.negative(`Failed to delete initiative. ${err.response?.data || 'Please try again.'}`)
        throw err
      } finally {
        this.loading.delete = false
      }
    },

    async markAccomplished(id, payload) {
      this.loading.accomplishment = true
      this.error.accomplishment = null

      try {
        let body = payload

        if (payload?.file_path) {
          body = new FormData()
          body.append('reporting_period', payload.reporting_period)
          body.append('file_path', payload.file_path)
        }

        const response = await api.post(`/pme/initiatives/${id}/accomplishments/`, body)
        notify.positive('Initiative marked as accomplished.')
        return response.data
      } catch (err) {
        this.error.accomplishment = err.response?.data || err.message
        notify.negative(
          `Failed to mark initiative as accomplished. ${err.response?.data || 'Please try again.'}`,
        )
        throw err
      } finally {
        this.loading.accomplishment = false
      }
    },

    async revertAccomplishment(id) {
      this.loading.accomplishment = true
      this.error.accomplishment = null

      try {
        await api.delete(`/pme/initiatives/${id}/accomplishments/`)
        notify.positive('Accomplishment reverted successfully.')
        return true
      } catch (err) {
        this.error.accomplishment = err.response?.data || err.message
        notify.negative(
          `Failed to revert accomplishment. ${err.response?.data || 'Please try again.'}`,
        )
        throw err
      } finally {
        this.loading.accomplishment = false
      }
    },
  },
})

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useInitiativeStore, import.meta.hot))
}
