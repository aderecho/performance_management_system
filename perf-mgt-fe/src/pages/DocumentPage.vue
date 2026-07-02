<template>
  <q-page class="bg-page q-pa-md">
    <PageComboHeader
      title="Documents"
      :breadcrumbs="[
          { label: 'Admin' }, 
          { label: 'Documents' }
          ]"
      :show-filter="false"
    >
      <template #buttons>
        <q-btn
          color="primary"
          icon="add"
          :label="$q.screen.lt.sm ? '' : 'Add New Initiative'"
          :disable="pmeDocumentStore.loading.document"
          @click="handleAddInitiative"
        >
          <q-tooltip>Add New Initiative</q-tooltip>
        </q-btn>
      </template>
    </PageComboHeader>

    <!-- ERROR -->
    <q-banner v-if="dashboardStore.error" class="bg-red-1 text-red-9 rounded-borders q-mb-md">
      <template #avatar>
        <q-icon name="error" color="red-7" />
      </template>
      Failed to load document summary. Please try again.
      <template #action>
        <q-btn flat color="red-9" label="Retry" @click="fetchSummary()" />
      </template>
    </q-banner>

    <!-- SUMMARY CARDS -->
    <div class="row q-col-gutter-md q-mb-md">
      <div v-for="card in summaryCards" :key="card.key" class="col-12 col-sm-6 col-lg-3">
        <q-card flat bordered class="bg-white rounded-3xl overflow-hidden full-height">
          <q-card-section class="q-pa-md">
            <div class="row items-center no-wrap justify-between">
              <div class="min-w-0">
                <q-skeleton v-if="isLoading" type="text" width="72px" class="text-3xl" />
                <div v-else class="text-3xl text-weight-bold text-dark">{{ card.value }}</div>

                <div class="text-caption text-blue-grey-8 q-mt-sm ellipsis">{{ card.label }}</div>
              </div>

              <div :class="['icon-soft', card.iconColor, card.iconBg]">
                <component :is="card.icon" :size="24" :stroke-width="2" />
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>

      <!-- FILTERS -->
      <DashboardFilters
        v-model="filters"
        :show-search="false"
        :select-filters="documentFilterFields"
        @change="fetchSummary"
      />

    <!-- OPEN DOCUMENT (INLINE) -->
    <q-card flat bordered class="bg-white shadow-1 rounded-3xl">
      <q-card-section class="q-pa-md">
        <div class="row items-start justify-between q-mb-md gap-2">
          <div class="min-w-0">
            <div class="text-h6 text-weight-bold text-dark">
              {{ selectedDocument ? pmeDocumentStore.documentWithItems.name || 'Document' : 'Open Document' }}
            </div>
            <div class="text-caption text-blue-grey-8">
              {{
                selectedDocument
                  ? pmeDocumentStore.documentWithItems.template_name || 'Performance measures'
                  : 'Select a document above to view its performance measures'
              }}
            </div>
          </div>

        </div>

        <!-- EMPTY: no document selected -->
        <div v-if="!selectedDocument" class="column flex-center text-grey-6 q-pa-xl q-gutter-sm">
          <q-icon name="description" size="48px" />
          <div class="text-subtitle1">No document selected</div>
          <div class="text-caption">Choose a document from the filter to open it here.</div>
        </div>

        <!-- LOADING -->
        <HierarchyTableSkeleton v-else-if="pmeDocumentStore.loading.document" />

        <!-- SUCCESS -->
        <HierarchyTable
          v-else-if="pmeDocumentStore.documentWithItems.items"
          :items="pmeDocumentStore.documentWithItems.items || []"
          :document-id="String(selectedDocument)"
          :document="pmeDocumentStore.documentWithItems"
          @open-initiatives="handleOpenInitiatives"
        />
      </q-card-section>
    </q-card>

    <!-- INITIATIVES -->
    <InitiativeListModal
      v-model="showInitiativeModal"
      :indicator="selectedIndicator"
      :initiatives="initiativeStore.initiatives"
      :can-change-initiative="canChangeInitiative"
      :can-delete-initiative="canDeleteInitiative"
      :can-submit-accomplishment="canCreateInitiativeAccomplishment"
      :can-revert-accomplishment="canDeleteInitiativeAccomplishment"
      @edit="handleEditInitiative"
      @accomplished="handleMarkAsAccomplished"
      @deleted="handleDeleteInitiative"
      @reverted="handleRevertAccomplishment"
    />

    <InitiativeFormModal
      v-model="showInitiativeFormModal"
      :items="pmeDocumentStore.documentWithItems.items || []"
      :initiative="selectedInitiative"
      :loading="initiativeStore.loading.save"
      @submitted="handleInitiativeSubmitted"
    />

    <AccomplishmentFormModal
      v-if="selectedInitiative"
      v-model="showAccomplishmentFormModal"
      :initiative="selectedInitiative"
      :reporting-periods="pmeDocumentStore.reportingPeriods"
      @submitted="handleAccomplishmentSubmitted"
    />
  </q-page>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useAuthStore } from 'src/stores/auth'
import { useDashboardStore } from 'src/stores/pme/dashboard'
import { usePmeDocumentStore } from 'src/stores/pme/pmeDocument'
import { useInitiativeStore } from 'src/stores/pme/initiative'
import PageComboHeader from 'src/components/PageComboHeader.vue'
import DashboardFilters from 'src/components/dashboard/DashboardFilters.vue'
import AccomplishmentFormModal from 'src/components/pme/AccomplishmentFormModal.vue'
import HierarchyTable from 'src/components/pme/HierarchyTable.vue'
import HierarchyTableSkeleton from 'src/components/pme/HierarchyTableSkeleton.vue'
import InitiativeFormModal from 'src/components/pme/InitiativeFormModal.vue'
import InitiativeListModal from 'src/components/pme/InitiativeListModal.vue'
import { Ruler, Target, CircleCheckBig, TriangleAlert } from 'lucide-vue-next'
import { notify } from 'src/utils/notify'

const authStore = useAuthStore()
const dashboardStore = useDashboardStore()
const pmeDocumentStore = usePmeDocumentStore()
const initiativeStore = useInitiativeStore()

const filters = ref({
  template: null,
  document: null,
  group: null,
})

const lastTemplate = ref(null)
const lastDocument = ref(null)
const lastGroup = ref(null)

const showInitiativeFormModal = ref(false)
const showInitiativeModal = ref(false)
const showAccomplishmentFormModal = ref(false)
const selectedIndicator = ref(null)
const selectedInitiative = ref(null)

const summary = computed(() => dashboardStore.dashboardSummary || {})
const isLoading = computed(() => dashboardStore.loading && !dashboardStore.dashboardSummary)
const selectedDocument = computed(() => filters.value.document || null)

const templateOptions = computed(() => summary.value.template_options || [])
const documentOptions = computed(() => {
  const options = summary.value.document_options || []

  if (!filters.value.template) {
    return options
  }

  return options.filter((option) => option.template === filters.value.template)
})
const groupOptions = computed(() => summary.value.group_options || summary.value.sra_options || [])
const groupFilterLabel = computed(() => summary.value.group_filter_label || 'Strategic Result Area')

const measureLabel = computed(() => pluralize(summary.value.measure_label || 'Performance Measure'))
const objectiveLabel = computed(() => pluralize(summary.value.card_label || 'Objective'))
const canChangeInitiative = computed(() =>
  authStore.canAccess({ requiredPermission: 'pme.change_initiative' }),
)
const canDeleteInitiative = computed(() =>
  authStore.canAccess({ requiredPermission: 'pme.delete_initiative' }),
)
const canCreateInitiativeAccomplishment = computed(() =>
  authStore.canAccess({ requiredPermission: 'pme.add_initiativeaccomplishment' }),
)
const canDeleteInitiativeAccomplishment = computed(() =>
  authStore.canAccess({ requiredPermission: 'pme.delete_initiativeaccomplishment' }),
)

const documentFilterFields = computed(() => [
  {
    name: 'template',
    label: 'Template',
    options: templateOptions.value,
    colClass: 'col-12 col-md-4',
  },
  {
    name: 'document',
    label: 'Document',
    options: documentOptions.value,
    colClass: 'col-12 col-md-4',
  },
  {
    name: 'group',
    label: groupFilterLabel.value,
    options: groupOptions.value,
    colClass: 'col-12 col-md-4',
  },
])

const summaryCards = computed(() => [
  {
    key: 'performance_measures',
    label: measureLabel.value,
    value: summary.value.performance_measures || 0,
    icon: Ruler,
    iconBg: 'bg-soft-blue',
    iconColor: 'text-blue-8',
  },
  {
    key: 'objectives',
    label: objectiveLabel.value,
    value: summary.value.objectives || 0,
    icon: Target,
    iconBg: 'bg-soft-purple',
    iconColor: 'text-purple-8',
  },
  {
    key: 'completed',
    label: 'Completed',
    value: summary.value.completed || 0,
    icon: CircleCheckBig,
    iconBg: 'bg-soft-green',
    iconColor: 'text-green-8',
  },
  {
    key: 'major_disruption',
    label: 'Major Disruption',
    value: summary.value.major_disruption || 0,
    icon: TriangleAlert,
    iconBg: 'bg-soft-red',
    iconColor: 'text-red-7',
  },
])

function pluralize(label) {
  if (!label) {
    return ''
  }

  return label.endsWith('s') ? label : `${label}s`
}

function resetInitiativeUi() {
  showInitiativeFormModal.value = false
  showInitiativeModal.value = false
  showAccomplishmentFormModal.value = false
  selectedIndicator.value = null
  selectedInitiative.value = null
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

async function loadDocument(documentId) {
  if (!documentId) {
    pmeDocumentStore.resetState()
    return
  }

  try {
    await pmeDocumentStore.fetchDocument(documentId)
    await pmeDocumentStore.fetchReportingPeriods(documentId)
  } catch {
    notify.negative('Failed to load document. Please try again.')
  }
}

async function refreshDocument() {
  if (!selectedDocument.value) return null

  try {
    return await pmeDocumentStore.fetchDocument(selectedDocument.value)
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
    await refreshSelectedInitiatives()
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

async function fetchSummary(nextFilters = filters.value) {
  const nextTemplate = nextFilters.template || null
  const templateChanged = nextTemplate !== lastTemplate.value
  // A template change invalidates the previously selected document and group.
  const nextDocument = templateChanged ? null : nextFilters.document || null
  const documentChanged = nextDocument !== lastDocument.value
  const nextGroup = templateChanged || documentChanged ? null : nextFilters.group || null
  const groupChanged = nextGroup !== lastGroup.value

  filters.value = {
    template: nextTemplate,
    document: nextDocument,
    group: nextGroup,
  }

  try {
    await dashboardStore.fetchDashboardSummary({
      template: nextTemplate || undefined,
      document: nextDocument || undefined,
      group: nextGroup || undefined,
    })
  } catch {
    notify.negative('Failed to load document summary. Please try again.')
  }

  if (documentChanged || groupChanged) {
    resetInitiativeUi()
    initiativeStore.resetInitiatives()
    pmeDocumentStore.setFilters({ item: nextGroup, show_all: false })
    await loadDocument(nextDocument)
  }

  lastTemplate.value = nextTemplate
  lastDocument.value = nextDocument
  lastGroup.value = nextGroup
}

onMounted(() => {
  fetchSummary()
})
</script>
