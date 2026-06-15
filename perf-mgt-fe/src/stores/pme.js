import { defineStore, acceptHMRUpdate } from 'pinia'
import { api } from 'boot/axios'
import { notify } from 'src/utils/notify'

export const usePmeStore = defineStore('pmeStore', {
    state: () => ({
        loading: false,
        documentWithItems: {},
        items: [],
        error: null,
        documentId: null,
        templateId: null,
        showInitiativeFormModal: false,
        showAccomplishmentFormModal: false,
        selectedIndicator: null,
        initiatives: [],
        barChartColumns: [],
        reportingPeriods: [],
        showInitiativeModal: false,
        selectedInitiative: null,
        dashboardSummary: null,
        filters: {
            item: null,
            // show_all: false
        }
    }),
    getters: {},
    actions: {
        openInitiatives(indicator) {
            this.selectedIndicator = indicator
            this.fetchInitiatives(indicator.id)
            this.showInitiativeModal = true
        },

        closeInitiatives() {
            this.showInitiativeModal = false
        },

        async fetchDocument(id) {
            this.loading = true

            try {
                const response = await api.get(
                    `/pme/documents/${id}/items/`,
                    {
                        params: {
                            item: this.filters.item,
                            // show_all: this.filters.show_all
                        }
                    }
                )

                this.documentWithItems = response.data

            } catch (err) {
                notify.negative(
                    `Failed to load document. ${err.response?.data?.message || 'Please try again.'
                    }`
                )
            } finally {
                this.loading = false
            }
        },

        async fetchReportingPeriods(documentId) {
            const res = await api.get('/pme/reporting-periods/', {
                params: { document: documentId }
            })
            this.reportingPeriods = res.data.map(rp => ({
                id: rp.id,
                label: `Period ${rp.period_number} (${rp.start_date} to ${rp.end_date})`
            }))
        },

        // INITIATIVES
        onAddInitiative() {
            this.selectedInitiative = null
            this.showInitiativeFormModal = true
        },

        async fetchInitiatives(indicatorId, params = {}) {
            this.loading = true

            try {
                const response = await api.get(`/pme/items/${indicatorId}/initiatives/`, { params })
                this.initiatives = response.data
            } catch (err) {
                notify.negative(
                    `Failed to load initiatives. ${err.response?.data?.message || 'Please try again.'}`
                )
            } finally {
                this.loading = false
            }
        },

        async createSubmission(payload) {
            this.loading = true

            try {
                await api.post('/pme/initiatives/', payload)

                notify.positive('Accomplishment submitted successfully.')
            } catch (err) {
                notify.negative(
                    `Failed to submit Initiative. ${err.response.data || 'Please try again.'}`
                )
            } finally {
                this.loading = false
            }
        },

        async updateInitiative(id, payload) {
            this.loading = true

            try {
                await api.put(`/pme/initiatives/${id}/`, payload)
                notify.positive('Initiative updated successfully.')
            } catch (err) {
                notify.negative(
                    `Failed to update initiative. ${err.response?.data || 'Please try again.'}`
                )
            } finally {
                this.loading = false
            }
        },

        onEditInitiative(row) {
            this.selectedInitiative = row
            this.showInitiativeFormModal = true
        },

        async removeInitiative(row) {
            this.initiatives = this.initiatives.filter(i => i.id !== row.id)

            await this.fetchDocument(row.document_id)
            notify.positive('Initiative removed successfully.')
        },

        // ACCOMPLISHMENTS
        onMarkAsAccomplished(row) {
            this.selectedInitiative = row
            this.showAccomplishmentFormModal = true
        },

        async onAccomplishmentSubmitted(documentId) {
            this.showAccomplishmentFormModal = false
            this.selectedInitiative = null

            await this.fetchInitiatives(this.selectedIndicator.id)
            await this.fetchDocument(documentId)

            notify.positive('Initiative marked as accomplished.')
        },

        async revertAccomplishment(row) {
            await this.fetchDocument(row.document_id)
            notify.positive('Accomplishment reverted successfully.')
        },

        // FILTERS
        setFilters(newFilters) {
            this.filters = { ...newFilters }
        },

        // DASHBOARD
        async fetchDashboardSummary(params = {}) {
            this.loading = true

            try {
                const response = await api.get('/pme/dashboard/summary/', { params })
                this.dashboardSummary = response.data
            } catch (err) {
                notify.negative(
                    `Failed to load dashboard summary. ${err.response?.data?.message || 'Please try again.'
                    }`
                )
            } finally {
                this.loading = false
            }
        }
    }
})

if (import.meta.hot) {
    import.meta.hot.accept(acceptHMRUpdate(usePmeStore, import.meta.hot))
}
