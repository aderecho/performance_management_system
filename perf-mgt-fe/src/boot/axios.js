import { defineBoot } from '#q-app/wrappers'
import axios from 'axios'

const api = axios.create({
  baseURL: process.env.API_BASE_URL || 'http://localhost:8000/api/v1',
  withCredentials: true,
})

let isRefreshing = false
let failedQueue = []

const processQueue = (error = null) => {
  failedQueue.forEach(promise => {
    if (error) {
      promise.reject(error)
    } else {
      promise.resolve()
    }
  })
  failedQueue = []
}

export default defineBoot(({ app, router }) => {
  app.config.globalProperties.$axios = axios
  app.config.globalProperties.$api = api

  api.interceptors.response.use(
    response => response,
    async error => {
      const originalRequest = error.config

      if (!error.response || !originalRequest) {
        return Promise.reject(error)
      }

      if (originalRequest.url.includes('/auth/refresh/')) {
        return Promise.reject(error)
      }

      if (error.response.status === 401) {
        if (isRefreshing) {

          return new Promise((resolve, reject) => {
            failedQueue.push({
              resolve: () => resolve(api(originalRequest)),
              reject
            })
          })
        }

        originalRequest._retry = true
        isRefreshing = true

        try {
          await api.post('/auth/refresh/')
          processQueue(null)
          return api(originalRequest)
        } catch (refreshError) {
          processQueue(refreshError)
          await api.post('/auth/logout/')
          router.push('/login')
          return Promise.reject(refreshError)
        } finally {
          isRefreshing = false
        }
      }

      return Promise.reject(error)
    }
  )
})

export { api }