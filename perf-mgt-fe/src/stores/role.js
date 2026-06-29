import { defineStore, acceptHMRUpdate } from 'pinia'
import { api } from 'src/boot/axios'

export const useRoleStore = defineStore('roleStore', {
  state: () => ({
    roles: [],
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
    options: (state) => state.roles.map((role) => ({
      label: role.name,
      value: role.id,
      ...role,
    })),
  },

  actions: {
    async fetchRoles() {
      this.loading.list = true
      this.error.list = null

      try {
        const response = await api.get('/auth/roles/')
        this.roles = response.data
        return response.data
      } catch (err) {
        this.error.list = err.response?.data || err.message
        throw err
      } finally {
        this.loading.list = false
      }
    },

    async createRole(payload) {
      this.loading.save = true
      this.error.save = null

      try {
        const response = await api.post('/auth/roles/', payload)
        this.roles.push(response.data)
        this.roles.sort((a, b) => a.name.localeCompare(b.name))
        return response.data
      } catch (err) {
        this.error.save = err.response?.data || err.message
        throw err
      } finally {
        this.loading.save = false
      }
    },

    async updateRole(id, payload) {
      this.loading.save = true
      this.error.save = null

      try {
        const response = await api.put(`/auth/roles/${id}/`, payload)
        const index = this.roles.findIndex((role) => role.id === id)

        if (index !== -1) {
          this.roles.splice(index, 1, response.data)
          this.roles.sort((a, b) => a.name.localeCompare(b.name))
        }

        return response.data
      } catch (err) {
        this.error.save = err.response?.data || err.message
        throw err
      } finally {
        this.loading.save = false
      }
    },

    async deleteRole(id) {
      this.loading.delete = true
      this.error.delete = null

      try {
        await api.delete(`/auth/roles/${id}/`)
        this.roles = this.roles.filter((role) => role.id !== id)
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
  import.meta.hot.accept(acceptHMRUpdate(useRoleStore, import.meta.hot))
}
