import { defineStore, acceptHMRUpdate } from 'pinia'
import { api } from 'src/boot/axios'

export const useUserStore = defineStore('userStore', {
    state: () => ({
        users: [],
        loading: false,
        error: null,
        stats: null
    }),
    getters: {},
    actions: {
        async fetchUsers() {
            try {
                const response = await api.get('/auth/users/')
                this.users = response.data
            } catch (err) {
                this.error = err.response?.data || err.message
            } finally {
                this.loading = false
            }
        },

        async createUser(payload) {
            this.loading = true
            this.error = null

            try {
                const response = await api.post('/auth/users/', payload)

                this.users.push(response.data)

                return response.data
            } catch (err) {
                this.error = err.response?.data || err.message
                throw err
            } finally {
                this.loading = false
            }
        },

        async fetchUserStats() {
            try {
                const response = await api.get('/auth/users/stats/')
                this.stats = response.data
            } catch (err) {
                this.error = err.response?.data || err.message
            } finally {
                this.loading = false
            }
        },
    }
})

if (import.meta.hot) {
    import.meta.hot.accept(acceptHMRUpdate(useUserStore, import.meta.hot))
}
