import { defineStore, acceptHMRUpdate } from 'pinia'
import { api } from 'src/boot/axios'

export const useCoreStore = defineStore('coreStore', {
  state: () => ({
    units: [],
    loading: false
  }),

  actions: {
    async fetchUnits() {
      this.loading = true
      try {
        const res = await api.get('/core/units/')
        this.units = res.data
      } finally {
        this.loading = false
      }
    }
  }
})

if (import.meta.hot) {
    import.meta.hot.accept(acceptHMRUpdate(useCoreStore, import.meta.hot))
}