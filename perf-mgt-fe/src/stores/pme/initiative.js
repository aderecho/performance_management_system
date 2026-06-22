import { defineStore, acceptHMRUpdate } from 'pinia'
import { api } from 'boot/axios'

let fetchInitiativesRequestKey = 0

export const useInitiativeStore = defineStore('initiativeStore', {
  state: () => ({
    initiativesByIndicator: {},
    currentIndicatorId: null,
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
    },
  }),

  getters: {
    initiatives: (state) => {
      if (!state.currentIndicatorId) return []

      return state.initiativesByIndicator[state.currentIndicatorId] || []
    },
  },

  actions: {
    resetInitiatives() {
      fetchInitiativesRequestKey += 1
      this.initiativesByIndicator = {}
      this.currentIndicatorId = null
      this.loading = {
        list: false,
        save: false,
        delete: false,
        accomplishment: false,
      }
      this.error = {
        list: null,
        save: null,
        delete: null,
        accomplishment: null,
      }
    },

    async fetchInitiatives(indicatorId, params = {}) {
      const requestKey = ++fetchInitiativesRequestKey
      this.loading.list = true
      this.error.list = null

      try {
        const response = await api.get(`/pme/items/${indicatorId}/initiatives/`, { params })

        if (requestKey !== fetchInitiativesRequestKey) {
          return response.data
        }

        this.currentIndicatorId = indicatorId
        this.initiativesByIndicator = {
          ...this.initiativesByIndicator,
          [indicatorId]: response.data,
        }

        return response.data
      } catch (err) {
        if (requestKey !== fetchInitiativesRequestKey) {
          return []
        }

        this.error.list = err.response?.data || err.message
        this.currentIndicatorId = indicatorId
        this.initiativesByIndicator = {
          ...this.initiativesByIndicator,
          [indicatorId]: [],
        }

        throw err
      } finally {
        if (requestKey === fetchInitiativesRequestKey) {
          this.loading.list = false
        }
      }
    },

    async createInitiative(payload) {
      this.loading.save = true
      this.error.save = null

      try {
        const response = await api.post('/pme/initiatives/', payload)
        const indicatorId = response.data.item ?? payload.item

        if (indicatorId && this.initiativesByIndicator[indicatorId]) {
          this.initiativesByIndicator = {
            ...this.initiativesByIndicator,
            [indicatorId]: [...this.initiativesByIndicator[indicatorId], response.data],
          }
        }

        return response.data
      } catch (err) {
        this.error.save = err.response?.data || err.message
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
        this.replaceCachedInitiative(id, response.data)
        return response.data
      } catch (err) {
        this.error.save = err.response?.data || err.message
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
        this.removeCachedInitiative(id)
        return true
      } catch (err) {
        this.error.delete = err.response?.data || err.message
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
        return response.data
      } catch (err) {
        this.error.accomplishment = err.response?.data || err.message
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
        return true
      } catch (err) {
        this.error.accomplishment = err.response?.data || err.message
        throw err
      } finally {
        this.loading.accomplishment = false
      }
    },

    replaceCachedInitiative(id, nextInitiative) {
      if (!nextInitiative?.id) return

      this.initiativesByIndicator = Object.fromEntries(
        Object.entries(this.initiativesByIndicator).map(([indicatorId, initiatives]) => [
          indicatorId,
          initiatives.map((initiative) => (initiative.id === id ? nextInitiative : initiative)),
        ]),
      )
    },

    removeCachedInitiative(id) {
      this.initiativesByIndicator = Object.fromEntries(
        Object.entries(this.initiativesByIndicator).map(([indicatorId, initiatives]) => [
          indicatorId,
          initiatives.filter((initiative) => initiative.id !== id),
        ]),
      )
    },
  },
})

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useInitiativeStore, import.meta.hot))
}
