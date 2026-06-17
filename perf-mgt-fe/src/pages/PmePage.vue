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
                :initiative="selectedInitiative" />

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
    return null
  }
}

async function refreshSelectedInitiatives() {
  if (selectedIndicator.value?.id) {
    try {
      return await initiativeStore.fetchInitiatives(selectedIndicator.value.id)
    } catch {
      return []
    }
  }

  return []
}

function handleFilter(filters) {
  pmeDocumentStore.setFilters(filters)
  refreshDocument()
}

function handleAddInitiative() {
  selectedInitiative.value = null
  showInitiativeFormModal.value = true
}

async function handleOpenInitiatives(indicator) {
  selectedIndicator.value = indicator

  try {
    await initiativeStore.fetchInitiatives(indicator.id)
    showInitiativeModal.value = true
  } catch {
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

async function handleInitiativeSubmitted() {
  showInitiativeFormModal.value = false
  selectedInitiative.value = null

  await refreshDocument()
  await refreshSelectedInitiatives()
}

async function handleDeleteInitiative(row) {
  try {
    await initiativeStore.deleteInitiative(row.id)
    await refreshDocument()
  } catch {
    // The store action already notified the user.
  }
}

async function handleAccomplishmentSubmitted(payload) {
  if (!selectedInitiative.value) return

  try {
    await initiativeStore.markAccomplished(selectedInitiative.value.id, payload)

    showAccomplishmentFormModal.value = false
    selectedInitiative.value = null

    await refreshDocument()
    await refreshSelectedInitiatives()
  } catch {
    // The store action already notified the user.
  }
}

async function handleRevertAccomplishment(row) {
  try {
    await initiativeStore.revertAccomplishment(row.id)
    await refreshDocument()
    await refreshSelectedInitiatives()
  } catch {
    // The store action already notified the user.
  }
}

watch(
    () => route.params.documentId,
    async (newId) => {
        if (newId) {
            resetInitiativeUi()
            pmeDocumentStore.clearDocumentState()

            try {
                await pmeDocumentStore.fetchDocument(newId)
            } catch {
                // The store action already notified the user.
            }

            try {
                await pmeDocumentStore.fetchReportingPeriods(newId)
            } catch {
                // The store action already notified the user.
            }
        }
    },
    { immediate: true }
)
</script>
