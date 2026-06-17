import { defineStore, acceptHMRUpdate } from 'pinia'
import { api } from 'boot/axios'
import { notify } from 'src/utils/notify'

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
    }
  }),

  actions: {
    clearDocumentState() {
      this.documentWithItems = {}
      this.reportingPeriods = []
    },

    setFilters(newFilters) {
      this.filters = { ...this.filters, ...newFilters }
    },

    async fetchDocument(documentId) {
      this.loading.document = true
      this.error.document = null

      try {
        const response = await api.get(`/pme/documents/${documentId}/items/`, {
          params: {
            item: this.filters.item,
            show_all: this.filters.show_all,
          },
        })

        this.documentWithItems = response.data
        return response.data
      } catch (err) {
        this.error.document = err.response?.data || err.message
        notify.negative(
          `Failed to load document. ${err.response?.data?.message || 'Please try again.'}`,
        )
        throw err
      } finally {
        this.loading.document = false
      }
    },

    async fetchReportingPeriods(documentId) {
      this.loading.reportingPeriods = true
      this.error.reportingPeriods = null

      try {
        const res = await api.get('/pme/reporting-periods/', {
          params: { document: documentId },
        })

        this.reportingPeriods = res.data.map((rp) => ({
          id: rp.id,
          label: `Period ${rp.period_number} (${rp.start_date} to ${rp.end_date})`,
        }))

        return this.reportingPeriods
      } catch (err) {
        this.error.reportingPeriods = err.response?.data || err.message
        notify.negative(
          `Failed to load reporting periods. ${err.response?.data?.message || 'Please try again.'}`,
        )
        throw err
      } finally {
        this.loading.reportingPeriods = false
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
        notify.negative(
          `Failed to load filter items. ${err.response?.data?.message || 'Please try again.'}`,
        )
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
