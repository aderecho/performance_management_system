import { Notify } from 'quasar'

export const notify = {
  positive (message, options = {}) {
    Notify.create({ type: 'positive', message, position: 'top-right', ...options })
  },

  negative (message, options = {}) {
    Notify.create({ type: 'negative', message, position: 'top-right', ...options })
  },

  info (message, options = {}) {
    Notify.create({ type: 'info', message, position: 'top-right', ...options })
  },

  warning (message, options = {}) {
    Notify.create({ type: 'warning', position: 'top-right', message, ...options })
  }
}