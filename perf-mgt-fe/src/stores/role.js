import { defineStore, acceptHMRUpdate } from 'pinia'
import { api } from 'src/boot/axios'

export const useRoleStore = defineStore('roleStore', {
  state: () => ({
    roles: [],
    loading: {
      list: false,
      save: false,
      status: false,
    },
    error: {
      list: null,
      save: null,
      status: null,
    },
  }),

  getters: {
    options: (state) => state.roles
      .filter((role) => !role.is_deleted)
      .map((role) => ({
        label: role.name,
        value: role.id,
        ...role,
      })),
    roleNamesByIds: (state) => (roleIds = []) => {
      const nameById = Object.fromEntries(state.roles.map((role) => [role.id, role.name]))
      const ids = Array.isArray(roleIds) ? roleIds : []
      return ids.map((id) => nameById[id]).filter(Boolean)
    },
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

    async setRoleStatus(id, isDelete) {
      this.loading.status = true
      this.error.status = null

      try {
        const response = await api.patch(`/auth/roles/${id}/`, { is_deleted: isDelete })
        const index = this.roles.findIndex((role) => role.id === id)

        if (index !== -1) {
          this.roles.splice(index, 1, response.data)
        } else {
          this.roles.push(response.data)
        }

        this.roles.sort((a, b) => a.name.localeCompare(b.name))

        return response.data
      } catch (err) {
        this.error.status = err.response?.data || err.message
        throw err
      } finally {
        this.loading.status = false
      }
    },

    setRoleInactive(id) {
      return this.setRoleStatus(id, true)
    },

    setRoleActive(id) {
      return this.setRoleStatus(id, false)
    },
  },
})

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useRoleStore, import.meta.hot))
}
