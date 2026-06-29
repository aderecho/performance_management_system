<template>
    <q-page class="flex q-pa-lg">
        <div class="full-width">


            <PageComboHeader :title="pmeDocumentStore.documentWithItems.template_name || ''"
            :breadcrumbs="[
                { label: 'Home', to: '/' },
                { label: pmeDocumentStore.documentWithItems.template_name || '' },
                { label: pmeDocumentStore.documentWithItems.name || '' }
            ]"
            @apply="handleFilter"
            @add-initiative="handleAddInitiative"
            >
                <!-- TITLE -->
                <template #title>
                    <q-skeleton v-if="pmeDocumentStore.loading.document" type="text" width="260px" />
                    <span v-else>
                        {{ pmeDocumentStore.documentWithItems.template_name }}
                    </span>
                </template>

                <!-- BREADCRUMB 1 -->
                <template #breadcrumb-0>
                    <span>Home</span>
                </template>

                <!-- BREADCRUMB 2 -->
                <template #breadcrumb-1>
                    <q-skeleton v-if="pmeDocumentStore.loading.document" type="text" width="140px" inline />
                    <span v-else>
                        {{ pmeDocumentStore.documentWithItems.template_name }}
                    </span>
                </template>

                <!-- BREADCRUMB 3 -->
                <template #breadcrumb-2>
                    <q-skeleton v-if="pmeDocumentStore.loading.document" type="text" width="160px" inline />
                    <span v-else>
                        {{ pmeDocumentStore.documentWithItems.name }}
                    </span>
                </template>
            </PageComboHeader>


            <HierarchyTable v-if="pmeDocumentStore.documentWithItems.items" :items="pmeDocumentStore.documentWithItems.items || []" :document-id="pmeDocumentStore.documentWithItems.id"
                :document="pmeDocumentStore.documentWithItems" @open-initiatives="handleOpenInitiatives" />

            <HierarchyTableSkeleton v-else-if="pmeDocumentStore.loading.document" />

            <InitiativeFormModal v-model="showInitiativeFormModal" :items="pmeDocumentStore.documentWithItems.items || []"
                :reporting-periods="pmeDocumentStore.reportingPeriods || []" @submitted="handleInitiativeSubmitted"
                :initiative="selectedInitiative" :loading="initiativeStore.loading.save" />

            <InitiativeListModal
                v-model="showInitiativeModal"
                :indicator="selectedIndicator"
                :initiatives="initiativeStore.initiatives"
                @edit="handleEditInitiative"
                @accomplished="handleMarkAsAccomplished"
                @deleted="handleDeleteInitiative"
                @reverted="handleRevertAccomplishment"
            />

            <AccomplishmentFormModal
                v-if="selectedInitiative"
                v-model="showAccomplishmentFormModal"
                :initiative="selectedInitiative"
                :reporting-periods="pmeDocumentStore.reportingPeriods"
                @submitted="handleAccomplishmentSubmitted"
            />

        </div>
    </q-page>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { usePmeDocumentStore } from 'src/stores/pme/pmeDocument'
import { useInitiativeStore } from 'src/stores/pme/initiative'
import { notify } from 'src/utils/notify'

import PageComboHeader from 'src/components/pme/PageComboHeader.vue'
import HierarchyTable from 'src/components/pme/HierarchyTable.vue'
import HierarchyTableSkeleton from 'src/components/pme/HierarchyTableSkeleton.vue'
import InitiativeListModal from 'src/components/pme/InitiativeListModal.vue'
import InitiativeFormModal from 'src/components/pme/InitiativeFormModal.vue'
import AccomplishmentFormModal from 'src/components/pme/AccomplishmentFormModal.vue'

const route = useRoute()

const pmeDocumentStore = usePmeDocumentStore()
const initiativeStore = useInitiativeStore()

const showInitiativeFormModal = ref(false)
const showInitiativeModal = ref(false)
const showAccomplishmentFormModal = ref(false)
const selectedIndicator = ref(null)
const selectedInitiative = ref(null)

function resetInitiativeUi() {
  showInitiativeFormModal.value = false
  showInitiativeModal.value = false
  showAccomplishmentFormModal.value = false
  selectedIndicator.value = null
  selectedInitiative.value = null
}

async function refreshDocument() {
  try {
    return await pmeDocumentStore.fetchDocument(route.params.documentId)
  } catch {
    notify.negative('Failed to load document. Please try again.')
    return null
  }
}

async function refreshSelectedInitiatives() {
  if (selectedIndicator.value?.id) {
    try {
      return await initiativeStore.fetchInitiatives(selectedIndicator.value.id)
    } catch {
      notify.negative('Failed to load initiatives. Please try again.')
      return []
    }
  }

  return []
}

function firstApiMessage(data) {
  if (!data) return null
  if (typeof data === 'string') return data
  if (Array.isArray(data)) return data.map(firstApiMessage).find(Boolean) || null
  if (typeof data === 'object') {
    return Object.values(data).map(firstApiMessage).find(Boolean) || null
  }

  return null
}

function apiErrorMessage(err, fallback) {
  return firstApiMessage(err?.response?.data) || fallback
}

async function handleFilter(filters) {
  pmeDocumentStore.setFilters(filters)
  await refreshDocument()
}

function handleAddInitiative() {
  selectedInitiative.value = null
  showInitiativeFormModal.value = true
}

async function handleOpenInitiatives(indicator) {
  selectedIndicator.value = indicator

  try {
    await initiativeStore.fetchInitiatives(indicator.id)

    if (selectedIndicator.value?.id !== indicator.id) return

    showInitiativeModal.value = true
  } catch {
    notify.negative('Failed to load initiatives. Please try again.')
    selectedIndicator.value = null
  }
}

function handleEditInitiative(row) {
  selectedInitiative.value = row
  showInitiativeFormModal.value = true
}

function handleMarkAsAccomplished(row) {
  selectedInitiative.value = row
  showAccomplishmentFormModal.value = true
}

async function handleInitiativeSubmitted(payload) {
  const initiative = selectedInitiative.value
  const isEdit = !!initiative

  try {
    if (isEdit) {
      await initiativeStore.updateInitiative(initiative.id, payload)
      notify.positive('Initiative updated successfully.')
    } else {
      await initiativeStore.createInitiative(payload)
      notify.positive('Initiative submitted successfully.')
    }

    showInitiativeFormModal.value = false
    selectedInitiative.value = null

    await refreshDocument()
    await refreshSelectedInitiatives()
  } catch (err) {
    notify.negative(
      apiErrorMessage(
        err,
        `Failed to ${isEdit ? 'update' : 'submit'} initiative. Please try again.`,
      ),
    )
  }
}

async function handleDeleteInitiative(row) {
  try {
    await initiativeStore.deleteInitiative(row.id)
    notify.positive('Initiative removed successfully.')
    await refreshDocument()
  } catch {
    notify.negative('Failed to delete initiative. Please try again.')
  }
}

async function handleAccomplishmentSubmitted(payload) {
  if (!selectedInitiative.value) return

  try {
    await initiativeStore.markAccomplished(selectedInitiative.value.id, payload)
    notify.positive('Initiative marked as accomplished.')

    showAccomplishmentFormModal.value = false
    selectedInitiative.value = null

    await refreshDocument()
    await refreshSelectedInitiatives()
  } catch {
    notify.negative('Failed to mark initiative as accomplished. Please try again.')
  }
}

async function handleRevertAccomplishment(row) {
  try {
    await initiativeStore.revertAccomplishment(row.id)
    notify.positive('Accomplishment reverted successfully.')
    await refreshDocument()
    await refreshSelectedInitiatives()
  } catch {
    notify.negative('Failed to revert accomplishment. Please try again.')
  }
}

watch(
    () => route.params.documentId,
    async (newId) => {
        if (newId) {
            resetInitiativeUi()
            pmeDocumentStore.resetState()
            initiativeStore.resetInitiatives()

            try {
                await pmeDocumentStore.fetchDocument(newId)
            } catch {
                notify.negative('Failed to load document. Please try again.')
            }

            try {
                await pmeDocumentStore.fetchReportingPeriods(newId)
            } catch {
                notify.negative('Failed to load reporting periods. Please try again.')
            }
        }
    },
    { immediate: true }
)
</script>
