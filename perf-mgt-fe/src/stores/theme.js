import { defineStore, acceptHMRUpdate } from 'pinia'
import { Dark } from 'quasar'

export const useThemeStore = defineStore('themeStore', {
  state: () => ({
    darkMode: false,
  }),

  actions: {
    setDarkMode(val) {
      this.darkMode = val
      Dark.set(val)
      localStorage.setItem('darkMode', val ? 'dark' : 'light')
    },

    toggleDarkMode() {
      this.setDarkMode(!this.darkMode)
    },

    initTheme() {
      const saved = localStorage.getItem('darkMode')
      this.darkMode = saved === 'dark'
      Dark.set(this.darkMode)
    },
  },
})

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useThemeStore, import.meta.hot))
}
