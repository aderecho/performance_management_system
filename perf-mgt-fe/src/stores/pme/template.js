import { defineStore, acceptHMRUpdate } from 'pinia'
import { api } from 'boot/axios'

export const usePmeTemplateStore = defineStore('pmeTemplateStore', {
  state: () => ({
    templates: [],
    templateNodeTypes: [],
    loading: {
      templates: false,
      templateNodeTypes: false,
    },
    error: {
      templates: null,
      templateNodeTypes: null,
    },
  }),

  actions: {
    resetState() {
      this.templates = []
      this.templateNodeTypes = []
      this.loading = {
        templates: false,
        templateNodeTypes: false,
      }
      this.error = {
        templates: null,
        templateNodeTypes: null,
      }
    },

    async fetchTemplates() {
      this.loading.templates = true
      this.error.templates = null

      try {
        const response = await api.get('/pme/templates/')
        this.templates = response.data
        return response.data
      } catch (err) {
        this.error.templates = err.response?.data || err.message
        throw err
      } finally {
        this.loading.templates = false
      }
    },
  },
})

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(usePmeTemplateStore, import.meta.hot))
}
