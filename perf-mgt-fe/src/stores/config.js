import { defineStore, acceptHMRUpdate } from 'pinia'
import { api } from 'src/boot/axios'
import { Dark } from 'quasar'

export const useConfigStore = defineStore('configStore', {
  state: () => ({
    templateList: [],
    templateNodeTypeList: [],
    darkMode: false,
  }),
  getters: {},
  actions: {
    async getTemplateList () {
      const response = await api.get("pme/templates/")
      this.templateList = response.data
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
