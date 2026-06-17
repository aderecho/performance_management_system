import { defineStore, acceptHMRUpdate } from 'pinia'
import { api } from 'src/boot/axios'
import { Dark } from 'quasar'

export const useConfigStore = defineStore('configStore', {
  state: () => ({
    templateList: [],
    templateNodeTypeList: [],
    darkMode: false,
    loading: {
      templates: false,
    },
    error: {
      templates: null,
    },
  }),
  getters: {},
  actions: {
    async getTemplateList () {
      this.loading.templates = true
      this.error.templates = null

      try {
        const response = await api.get("pme/templates/")
        this.templateList = response.data
        return response.data
      } catch (err) {
        this.error.templates = err.response?.data || err.message
        throw err
      } finally {
        this.loading.templates = false
      }
    },

    // async getTemplateNodeTypeList () {
    //   const response = await api.get("pme/template-node-types")
    //   this.templateNodeTypeList = response.data
    // },

    setDarkMode (val) {
      this.darkMode = val
      Dark.set(val)
      localStorage.setItem('darkMode', val ? 'dark' : 'light')
    },

    toggleDarkMode () {
      this.setDarkMode(!this.darkMode)
    },

    initTheme () {
      const saved = localStorage.getItem('darkMode')
      this.darkMode = saved === 'dark'
      Dark.set(this.darkMode)
    }

  }
})

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useConfigStore, import.meta.hot))
}
