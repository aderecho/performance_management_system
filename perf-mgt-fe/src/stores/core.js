import { defineStore, acceptHMRUpdate } from 'pinia'
import { api } from 'src/boot/axios'

export const useCoreStore = defineStore('coreStore', {
  state: () => ({
    units: [],
    loading: {
      units: false,
    },
    error: {
      units: null,
    }
  }),

  actions: {
    async fetchUnits() {
      this.loading.units = true
      this.error.units = null
      try {
        const res = await api.get('/core/units/')
        this.units = res.data
        return res.data
      } catch (err) {
        this.error.units = err.response?.data || err.message
        throw err
      } finally {
        this.loading.units = false
      }
    }
  }
})

if (import.meta.hot) {
    import.meta.hot.accept(acceptHMRUpdate(useCoreStore, import.meta.hot))
}
