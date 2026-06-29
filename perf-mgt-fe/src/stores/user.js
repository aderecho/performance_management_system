import { defineStore, acceptHMRUpdate } from 'pinia'
import { api } from 'src/boot/axios'

export const useUserStore = defineStore('userStore', {
    state: () => ({
        users: [],
        loading: {
            list: false,
            stats: false,
            save: false,
            delete: false,
        },
        error: {
            list: null,
            stats: null,
            save: null,
            delete: null,
        },
        stats: null
    }),
    getters: {},
    actions: {
        async fetchUsers(payload) {
            this.loading.list = true
            this.error.list = null

            try {
                const response = await api.get('/auth/users/', {params: payload})
                this.users = response.data
                return response.data
            } catch (err) {
                this.error.list = err.response?.data || err.message
                throw err
            } finally {
                this.loading.list = false
            }
        },

        async createUser(payload) {
            this.loading.save = true
            this.error.save = null

            try {
                const response = await api.post('/auth/users/create/', payload)

                this.users.push(response.data)

                return response.data
            } catch (err) {
                this.error.save = err.response?.data || err.message
                throw err
            } finally {
                this.loading.save = false
            }
        },

        async updateUser(id, payload) {
            this.loading.save = true
            this.error.save = null

            try {
                const response = await api.put(`/auth/users/${id}/`, payload)
                const index = this.users.findIndex(user => user.id === id)

                if (index !== -1) {
                    this.users.splice(index, 1, response.data)
                }

                return response.data
            } catch (err) {
                this.error.save = err.response?.data || err.message
                throw err
            } finally {
                this.loading.save = false
            }
        },

        async updateUserPermissions(id, permissionIds) {
            this.loading.save = true
            this.error.save = null

            try {
                const response = await api.patch(`/auth/users/${id}/`, {
                    user_permission_ids: permissionIds,
                })
                const index = this.users.findIndex(user => user.id === id)

                if (index !== -1) {
                    this.users.splice(index, 1, response.data)
                }

                return response.data
            } catch (err) {
                this.error.save = err.response?.data || err.message
                throw err
            } finally {
                this.loading.save = false
            }
        },

        async setUserActive(id, isActive) {
            this.loading.delete = true
            this.error.delete = null

            try {
                const response = await api.patch(`/auth/users/${id}/`, { is_active: isActive })
                const index = this.users.findIndex(user => user.id === id)

                if (index !== -1) {
                    this.users.splice(index, 1, response.data)
                }

                return response.data
            } catch (err) {
                this.error.delete = err.response?.data || err.message
                throw err
            } finally {
                this.loading.delete = false
            }
        },

        deactivateUser(id) {
            return this.setUserActive(id, false)
        },

        activateUser(id) {
            return this.setUserActive(id, true)
        },

        async fetchUserStats() {
            this.loading.stats = true
            this.error.stats = null

            try {
                const response = await api.get('/auth/users/stats/')
                this.stats = response.data
                return response.data
            } catch (err) {
                this.error.stats = err.response?.data || err.message
                throw err
            } finally {
                this.loading.stats = false
            }
        },
    }
})

if (import.meta.hot) {
    import.meta.hot.accept(acceptHMRUpdate(useUserStore, import.meta.hot))
}
