<template>
  <div class="q-pa-md">
    <PageComboHeader
      title="Archived Initiatives"
      :breadcrumbs="[
        { label: 'Home', to: '/admin/dashboard' },
        { label: 'Admin' },
        { label: 'Archived' },
        { label: 'Initiative' },
      ]"
      :can-add-initiative="false"
    />

    <!-- LOADING -->
    <div v-if="loading" class="flex flex-center q-pa-xl">
      <q-spinner size="42px" color="primary" />
    </div>

    <!-- ERROR -->
    <q-banner v-else-if="error" class="bg-red-1 text-red-9 rounded-borders">
      <template #avatar>
        <q-icon name="error" color="red-7" />
      </template>
      Failed to load archived initiatives. Please try again.
      <template #action>
        <q-btn flat color="red-9" label="Retry" @click="loadArchivedInitiatives" />
      </template>
    </q-banner>

    <!-- EMPTY -->
    <div
      v-else-if="!initiatives.length"
      class="column flex-center text-grey-6 q-pa-xl q-gutter-sm"
    >
      <q-icon name="inventory_2" size="48px" />
      <div class="text-subtitle1">No archived initiatives</div>
      <div class="text-caption">Initiatives that get archived will appear here.</div>
    </div>

    <!-- SUCCESS -->
    <q-table
      v-else
      :rows="initiatives"
      :columns="columns"
      row-key="id"
      flat
      bordered
      :rows-per-page-options="[10, 25, 50]"
    />
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import PageComboHeader from 'src/components/pme/PageComboHeader.vue'

const initiatives = ref([])
const loading = ref(false)
const error = ref(false)

const columns = [
  { name: 'description', label: 'Description', field: 'description', align: 'left', sortable: true },
  { name: 'target_date', label: 'Target Date', field: 'target_date', align: 'left', sortable: true },
  { name: 'value', label: 'Value', field: 'value', align: 'right', sortable: true },
  { name: 'remarks', label: 'Remarks', field: 'remarks', align: 'left' },
]

// Isolated data source for archived initiatives. The backend does not yet expose
// an archived-initiatives endpoint, so this resolves to an empty list and the page
// renders the empty state. Point this at the real endpoint (single change) once the
// backend archive flag / filtered endpoint is available.
async function fetchArchivedInitiatives() {
  return []
}

async function loadArchivedInitiatives() {
  loading.value = true
  error.value = false

  try {
    initiatives.value = await fetchArchivedInitiatives()
  } catch {
    error.value = true
    initiatives.value = []
  } finally {
    loading.value = false
  }
}

onMounted(loadArchivedInitiatives)
</script>
