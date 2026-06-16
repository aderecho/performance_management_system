<style>
.wrap-table .q-table__middle table {
  table-layout: fixed;
  width: 100%;
}
.wrap-table td.wrap-cell,
.wrap-table td.wrap-cell .q-td,
.wrap-table td.wrap-cell .q-td > div {
  white-space: normal !important;
  word-break: break-word !important;
  overflow-wrap: anywhere !important;
}
</style>
<template>
  <q-dialog :model-value="modelValue" @update:model-value="updateDialog">
    <q-card style="width: 1000px; max-width: 90vw;">
      <q-card-section class="q-mb-none">
        <div class="text-h6">Initiatives</div>
        <div class="text-caption text-grey">{{ indicator?.code }} {{ indicator?.name }}</div>
      </q-card-section>

      <q-card-section>
        <q-table v-if="initiatives && initiatives.length" class="q-pa-none q-ma-none wrap-table" :rows="initiatives" :columns="columns" row-key="id">

          <template #body-cell-is_accomplished="props">
            <q-td align="center">
              <q-avatar
                outline
                size="sm"
                :color="props.value ? 'green' : 'red'"
                text-color="white"
                :icon="props.value? 'check' : 'close'"
              />
            </q-td>
          </template>

          <template #body-cell-actions="props">
            <q-td align="center">
              <q-btn
                dense
                flat
                round
                :icon="!props.row.accomplishment ? 'task_alt' : 'cancel'"
                color="accent"
                @click="onMarkAsAccomplished(props.row)"
              >
                <q-tooltip>{{ !props.row.accomplishment ? 'Mark as Accomplished' : 'Revert'}}</q-tooltip>
              </q-btn>
            
              <q-btn
                dense
                flat
                round
                icon="edit"
                color="secondary"
                @click="editInitiative(props.row)"
              >
                <q-tooltip>Edit</q-tooltip>
              </q-btn>

              <q-btn
                dense
                flat
                round
                icon="delete"
                color="negative"
                @click="onDeleteClick(props.row)"
              >
                <q-tooltip>Delete</q-tooltip>
              </q-btn>
            </q-td>
          </template>
        </q-table>

        <div v-else class="text-grey text-center q-pa-md">
          No initiatives found.
        </div>
      </q-card-section>

      <q-card-actions align="right">
        <q-btn flat label="Close" color="primary" @click="close" />
      </q-card-actions>
    </q-card>

    <DeleteConfirmDialog
      v-model="showDeleteDialog"
      @confirmDelete="confirmDelete"
    >
      Are you sure you want to delete this initiative?
    </DeleteConfirmDialog>

    <RevertConfirmDialog
      v-model="showRevertDialog"
      @confirmRevert="confirmRevert"
    >
      Are you sure you want to revert this accomplishment?
    </RevertConfirmDialog>
  </q-dialog>
</template>

<script setup>
import { ref } from 'vue'
import { api } from 'boot/axios'
import DeleteConfirmDialog from 'src/components/DeleteConfirmDialog.vue'
import RevertConfirmDialog from 'src/components/RevertConfirmDialog.vue'
// import { isTrue } from 'src/utils/isTrue';

defineProps({
  modelValue: Boolean,
  indicator: { type: Object, default: () => {} },
  initiatives: { type: Array, default: () => [] },
})

const emit = defineEmits([
  'update:modelValue',
  'edit',
  'deleted',
  'accomplished',
  'reverted',
])

const columns = ref([
  { name: 'initiative', required: true, label: 'Initiative', align: 'left', field: row => row.description, format: val => `${val}`, sortable: true, style: 'width: 30%;', classes: 'wrap-cell' },
  { name: 'unit', required: true, label: 'Unit', align: 'center', field: row => row.unit?.short_code, format: val => `${val}`, sortable: false },
  { name: 'target_date', align: 'center', label: 'Target Date', field: row => row.target_date, format: val => `${val}`, sortable: false },
  { name: 'actual_value', align: 'center', label: 'Actual Value', field: row => row.value, format: val => `${val}`, sortable: false },
  { name: 'is_accomplished', align: 'center', label: 'Status', field: row => row.is_accomplished, sortable: false },
  { name: 'reporting_period', align: 'center', label: 'Reporting Period', field: row => formatReportingPeriod(row.accomplishment), sortable: false, style: 'width: 25%;', classes: 'wrap-cell' },
  { name: 'actions', label: 'Actions', align: 'center', sortable: false},
])

const formatReportingPeriod = (row) => {
  const rp = row?.reporting_period_detail
  if (!rp) return '---'

  return `Period ${rp.period_number} (${rp.start_date} to ${rp.end_date})`
}

const updateDialog = (val) => {
  emit("update:modelValue", val)
}

const close = () => {
  emit("update:modelValue", false)
}

// Edit
const editInitiative = row => {
  emit('edit', row)
}

// Delete
const showDeleteDialog = ref(false)
const showRevertDialog = ref(false)
const selectedInitiative = ref(null)

const onDeleteClick = (row) => {
  selectedInitiative.value = row
  showDeleteDialog.value = true
}

// Mark as accomplished
const onMarkAsAccomplished = async(row) => {
  // Mark as Accomplished
  if (!row.accomplishment) {
    emit('accomplished', row)
    return
  }

  // Revert Accomplishment
  try {
    selectedInitiative.value = row
    showRevertDialog.value = true
  } catch (err) {
    console.error('Failed to revert accomplishment', err)
  }
}

const confirmDelete = async () => {
  try {
    await api.delete(`/pme/initiatives/${selectedInitiative.value.id}/`)
    showDeleteDialog.value = false
    emit('deleted', selectedInitiative.value)
  } catch {
    // 
  }
}

const confirmRevert = async () => {
  try {
    const row = selectedInitiative.value
    if (!row) return

    await api.delete(`/pme/initiatives/${selectedInitiative.value.id}/accomplishments/`)

    showRevertDialog.value = false
    row.accomplishment = null
    row.is_accomplished = false
    row.reporting_period_detail = null

    emit('reverted', selectedInitiative.value)
  } catch {
    // 
  }
}
</script>
