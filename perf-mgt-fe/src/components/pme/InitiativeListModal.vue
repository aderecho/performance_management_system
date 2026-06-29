<template>
  <q-dialog :model-value="modelValue" @update:model-value="updateDialog">
    <q-card class="dialog-lg initiative-list-dialog rounded-borders">
      <q-card-section class="q-mb-none">
        <div class="text-h6">Initiatives</div>
        <div class="text-caption text-grey-8">{{ indicator?.code }} {{ indicator?.name }}</div>
      </q-card-section>

      <q-card-section>
        <q-table
          v-if="initiatives && initiatives.length"
          flat bordered
          class="q-pa-none q-ma-none wrap-table"
          table-header-class="bg-surface text-white"
          :rows="initiatives"
          :columns="columns"
          row-key="id"
        >
          <template #body-cell-is_accomplished="props">
            <q-td align="center">
              <q-avatar
                outline
                size="xs"
                :color="props.value ? 'green' : 'red'"
                text-color="white"
              >
                <Check v-if="props.value" :size="12" :stroke-width="5" />
                <X v-else :size="12" :stroke-width="3" />
              </q-avatar>
            </q-td>
          </template>

          <template #body-cell-evidence="props">
            <q-td align="center">
              <q-btn
                v-if="props.row.accomplishment?.file_url"
                dense
                flat
                round
                color="primary"
                type="a"
                :href="props.row.accomplishment.file_url"
                target="_blank"
              >
                <FileCheck2 :size="18" :stroke-width="2" />
                <q-tooltip>
                  {{ props.row.accomplishment.file_name || 'View evidence' }}
                </q-tooltip>
              </q-btn>

              <span v-else class="text-grey-6">---</span>
            </q-td>
          </template>

          <template #body-cell-actions="props">
            <q-td align="center">
              <q-btn
                dense
                flat
                round
                color="dark-grey"
                @click="onMarkAsAccomplished(props.row)"
              >
                <ClipboardCheck  v-if="!props.row.is_accomplished" :size="18" :stroke-width="2" />
                <RotateCcw v-else :size="18" :stroke-width="2" />
                <q-tooltip>{{
                  !props.row.is_accomplished ? 'Mark as Accomplished' : 'Revert'
                }}</q-tooltip>
              </q-btn>

              <q-btn
                dense
                flat
                round
                color="dark-grey"
                :disable="!getEvidenceHistory(props.row).length"
                @click="openHistory(props.row)"
              >
                <History :size="18" :stroke-width="2" />
                <q-tooltip>View history</q-tooltip>
              </q-btn>

              <q-btn
                dense
                flat
                round
                color="secondary"
                @click="editInitiative(props.row)"
              >
                <SquarePen :size="18" :stroke-width="2" />
                <q-tooltip>Edit</q-tooltip>
              </q-btn>

              <q-btn
                dense
                flat
                round
                color="negative"
                @click="onDeleteClick(props.row)"
              >
                <Trash2 :size="18" :stroke-width="2" />
                <q-tooltip>Delete</q-tooltip>
              </q-btn>
            </q-td>
          </template>
        </q-table>

        <div v-else class="text-grey text-center q-pa-md">No initiatives found.</div>
      </q-card-section>

      <q-card-actions align="right">
        <q-btn flat label="Close" color="primary" @click="close" />
      </q-card-actions>
    </q-card>

    <DeleteConfirmDialog v-model="showDeleteDialog" @confirmDelete="confirmDelete">
      Are you sure you want to delete this initiative?
    </DeleteConfirmDialog>

    <RevertConfirmDialog v-model="showRevertDialog" @confirmRevert="confirmRevert">
      Are you sure you want to revert this accomplishment?
    </RevertConfirmDialog>

    <q-dialog v-model="showHistoryDialog">
      <q-card class="history-dialog rounded-borders">
        <q-card-section>
          <div class="text-h6">Initiative History</div>
          <div class="text-caption text-grey-8">{{ selectedHistoryInitiative?.description }}</div>
        </q-card-section>

        <q-card-section>
          <q-markup-table
            v-if="selectedHistory.length"
            flat
            bordered
            class="wrap-table history-table"
          >
            <thead>
              <tr>
                <th class="text-left">Evidence</th>
                <th class="text-center">Status</th>
                <th class="text-center">Uploaded</th>
                <th class="text-center">Updated</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in selectedHistory" :key="item.id">
                <td>
                  <q-btn
                    v-if="item.file_url"
                    flat
                    dense
                    no-caps
                    color="primary"
                    type="a"
                    :href="item.file_url"
                    target="_blank"
                    class="q-pa-none"
                  >
                    {{ item.file_name || 'View evidence' }}
                  </q-btn>
                  <span v-else class="text-grey-6">---</span>
                </td>
                <td class="text-center">
                  <q-chip
                    dense
                    square
                    :color="historyStatusColor(item.status)"
                    text-color="white"
                  >
                    {{ item.status_label || historyStatusLabel(item.status) }}
                  </q-chip>
                </td>
                <td class="text-center">{{ formatDateTime(item.created_at) }}</td>
                <td class="text-center">{{ formatDateTime(item.updated_at) }}</td>
              </tr>
            </tbody>
          </q-markup-table>

          <div v-else class="text-grey text-center q-pa-md">No evidence history found.</div>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Close" color="primary" v-close-popup />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-dialog>
</template>

<script setup>
import { ref } from 'vue'
import DeleteConfirmDialog from 'src/components/DeleteConfirmDialog.vue'
import RevertConfirmDialog from 'src/components/RevertConfirmDialog.vue'
import { Check, FileCheck2, ClipboardCheck, History, RotateCcw, SquarePen, Trash2, X } from 'lucide-vue-next'

defineProps({
  modelValue: Boolean,
  indicator: { type: Object, default: () => ({}) },
  initiatives: { type: Array, default: () => [] },
})

const emit = defineEmits(['update:modelValue', 'edit', 'deleted', 'accomplished', 'reverted'])

const columns = ref([
  {
    name: 'initiative',
    required: true,
    label: 'Initiative',
    align: 'left',
    field: (row) => row.description,
    format: (val) => `${val}`,
    sortable: true,
    classes: 'wrap-cell initiative-col',
    headerClasses: 'initiative-col',
  },
  {
    name: 'unit',
    required: true,
    label: 'Unit',
    align: 'center',
    field: (row) => row.unit?.short_code,
    format: (val) => `${val}`,
    sortable: false,
  },
  {
    name: 'target_date',
    align: 'center',
    label: 'Target Date',
    field: (row) => row.target_date,
    format: (val) => `${val}`,
    sortable: false,
  },
  {
    name: 'actual_value',
    align: 'center',
    label: 'Actual Value',
    field: (row) => row.value,
    format: (val) => `${val}`,
    sortable: false,
  },
  {
    name: 'is_accomplished',
    align: 'center',
    label: 'Status',
    field: (row) => row.is_accomplished,
    sortable: false,
  },
  {
    name: 'reporting_period',
    align: 'center',
    label: 'Reporting Period',
    field: (row) => formatReportingPeriod(row.accomplishment),
    sortable: false,
    classes: 'wrap-cell reporting-period-col',
    headerClasses: 'reporting-period-col',
  },
  {
    name: 'evidence',
    align: 'center',
    label: 'Evidence',
    field: (row) => row.accomplishment?.file_url,
    sortable: false,
  },
  { name: 'actions', label: 'Actions', align: 'center', sortable: false },
])

const formatReportingPeriod = (row) => {
  const rp = row?.reporting_period_detail
  if (!rp) return '---'

  return `Period ${rp.period_number} (${rp.start_date} to ${rp.end_date})`
}

const updateDialog = (val) => {
  emit('update:modelValue', val)
}

const close = () => {
  emit('update:modelValue', false)
}

// Edit
const editInitiative = (row) => {
  emit('edit', row)
}

// Delete
const showDeleteDialog = ref(false)
const showRevertDialog = ref(false)
const showHistoryDialog = ref(false)
const selectedInitiative = ref(null)
const selectedHistoryInitiative = ref(null)
const selectedHistory = ref([])

const onDeleteClick = (row) => {
  selectedInitiative.value = row
  showDeleteDialog.value = true
}

// Mark as accomplished
const onMarkAsAccomplished = async (row) => {
  // Mark as Accomplished
  if (!row.is_accomplished) {
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
  showDeleteDialog.value = false
  emit('deleted', selectedInitiative.value)
}

const confirmRevert = async () => {
  if (!selectedInitiative.value) return

  showRevertDialog.value = false
  emit('reverted', selectedInitiative.value)
}

const getEvidenceHistory = (row) => row.accomplishment?.evidence_history || []

const openHistory = (row) => {
  selectedHistoryInitiative.value = row
  selectedHistory.value = getEvidenceHistory(row)
  showHistoryDialog.value = true
}

const historyStatusColor = (status) => (status === 1 ? 'positive' : 'grey-7')

const historyStatusLabel = (status) => (status === 1 ? 'Active' : 'Reverted')

const formatDateTime = (value) => {
  if (!value) return '---'

  return new Date(value).toLocaleString()
}
</script>

<style scoped>
.initiative-list-dialog {
  max-width: 95vw;
  width: 1100px;
}

.history-dialog {
  max-width: 92vw;
  width: 760px;
}

.history-table {
  max-height: 60vh;
}

.history-table thead tr th {
  background-color: #fff;
  position: sticky;
  top: 0;
  z-index: 1;
}
</style>
