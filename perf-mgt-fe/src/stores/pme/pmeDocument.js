import { defineStore, acceptHMRUpdate } from 'pinia'
import { api } from 'boot/axios'

let fetchDocumentRequestKey = 0
let fetchReportingPeriodsRequestKey = 0

export const usePmeDocumentStore = defineStore('pmeDocumentStore', {
  state: () => ({
    documentWithItems: {},
    reportingPeriods: [],
    filters: {
      item: null,
      show_all: false,
    },
    loading: {
      document: false,
      reportingPeriods: false,
      filterItems: false,
    },
    error: {
      document: null,
      reportingPeriods: null,
      filterItems: null,
    },
  }),

  actions: {
    resetState() {
      fetchDocumentRequestKey += 1
      fetchReportingPeriodsRequestKey += 1
      this.documentWithItems = {}
      this.reportingPeriods = []
      this.filters = {
        item: null,
        show_all: false,
      }
      this.loading = {
        document: false,
        reportingPeriods: false,
        filterItems: false,
      }
      this.error = {
        document: null,
        reportingPeriods: null,
        filterItems: null,
      }
    },

    setFilters(newFilters) {
      this.filters = { ...this.filters, ...newFilters }
    },

    async fetchDocument(documentId) {
      const requestKey = ++fetchDocumentRequestKey
      this.loading.document = true
      this.error.document = null

      try {
        const response = await api.get(`/pme/documents/${documentId}/items/`, {
          params: {
            item: this.filters.item,
            show_all: this.filters.show_all,
          },
        })

        if (requestKey !== fetchDocumentRequestKey) {
          return response.data
        }

        this.documentWithItems = response.data
        return response.data
      } catch (err) {
        if (requestKey !== fetchDocumentRequestKey) {
          return null
        }

        this.error.document = err.response?.data || err.message
        throw err
      } finally {
        if (requestKey === fetchDocumentRequestKey) {
          this.loading.document = false
        }
      }
    },

    async fetchReportingPeriods(documentId) {
      const requestKey = ++fetchReportingPeriodsRequestKey
      this.loading.reportingPeriods = true
      this.error.reportingPeriods = null

      try {
        const res = await api.get('/pme/reporting-periods/', {
          params: { document: documentId },
        })

        if (requestKey !== fetchReportingPeriodsRequestKey) {
          return []
        }

        this.reportingPeriods = res.data.map((rp) => ({
          id: rp.id,
          label: `Period ${rp.period_number} (${rp.start_date} to ${rp.end_date})`,
        }))

        return this.reportingPeriods
      } catch (err) {
        if (requestKey !== fetchReportingPeriodsRequestKey) {
          return []
        }

        this.error.reportingPeriods = err.response?.data || err.message
        throw err
      } finally {
        if (requestKey === fetchReportingPeriodsRequestKey) {
          this.loading.reportingPeriods = false
        }
      }
    },

    async fetchFilterItems(documentId, parentId = null) {
      this.loading.filterItems = true
      this.error.filterItems = null

      try {
        const response = await api.get('/pme/items/', {
          params: {
            document: documentId,
            parent: parentId,
          },
        })

        return response.data
      } catch (err) {
        this.error.filterItems = err.response?.data || err.message
        throw err
      } finally {
        this.loading.filterItems = false
      }
    },
  },
})

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(usePmeDocumentStore, import.meta.hot))
}
