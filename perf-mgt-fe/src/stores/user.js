import { defineStore, acceptHMRUpdate } from 'pinia'
import { api } from 'src/boot/axios'

export const useUserStore = defineStore('userStore', {
    state: () => ({
        users: [],
        loading: {
            list: false,
            stats: false,
            save: false,
        },
        error: {
            list: null,
            stats: null,
            save: null,
        },
        stats: null
    }),
    getters: {},
    actions: {
        async fetchUsers() {
            this.loading.list = true
            this.error.list = null

            try {
                const response = await api.get('/auth/users/')
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
                const response = await api.post('/auth/users/', payload)

                this.users.push(response.data)

                return response.data
            } catch (err) {
                this.error.save = err.response?.data || err.message
                throw err
            } finally {
                this.loading.save = false
            }
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
