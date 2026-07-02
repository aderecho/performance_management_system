<template>
  <q-dialog :model-value="modelValue" @update:model-value="updateDialog">
    <q-card class="pme-initiative-list-dialog rounded-lg shadow-8">
      <!-- HEADER -->
      <q-card-section class="row items-center no-wrap q-pa-md">
        <div class="pme-initiative-header-icon">
          <ListChecks :size="20" :stroke-width="2.2" />
        </div>
        <div class="min-w-0 q-ml-md col">
          <div class="text-h6 text-weight-bold leading-snug">Initiatives</div>
          <div class="text-caption text-blue-grey-6 pme-break-anywhere">
            {{ indicator?.code }} {{ indicator?.name }}
          </div>
        </div>
        <q-badge outline color="primary" class="flex-none q-mr-sm">
          {{ initiatives.length }} {{ initiatives.length === 1 ? 'initiative' : 'initiatives' }}
        </q-badge>
        <q-btn flat round dense icon="close" color="grey-7" class="flex-none" @click="close">
          <q-tooltip>Close</q-tooltip>
        </q-btn>
      </q-card-section>

      <q-separator />

      <!-- BODY -->
      <q-card-section class="pme-initiative-list-body">
        <div class="pme-initiative-list-panel bg-white rounded-lg">
          <q-table
            v-if="initiatives && initiatives.length"
            flat
            class="pme-initiative-list-table"
            :rows="initiatives"
            :columns="columns"
            row-key="id"
          >
            <template #body-cell-is_accomplished="props">
              <q-td align="center">
                <q-badge
                  rounded
                  class="pme-status-badge"
                  :class="props.value ? 'pme-status-badge--done' : 'pme-status-badge--pending'"
                >
                  <Check v-if="props.value" :size="12" :stroke-width="3" class="q-mr-xs" />
                  <X v-else :size="12" :stroke-width="3" class="q-mr-xs" />
                  {{ props.value ? 'Accomplished' : 'Pending' }}
                </q-badge>
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
                  v-if="actionPermission(props.row)"
                  dense
                  flat
                  round
                  color="dark-grey"
                  @click="onMarkAsAccomplished(props.row)"
                >
                  <ClipboardCheck v-if="!props.row.is_accomplished" :size="18" :stroke-width="2" />
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
                  v-if="canChangeInitiative"
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
                  v-if="canDeleteInitiative"
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

          <div v-else class="column items-center text-center q-pa-xl">
            <ListChecks :size="36" :stroke-width="1.8" class="text-grey-5" />
            <div class="text-weight-medium text-grey-8 q-mt-sm">No initiatives found</div>
            <div class="text-caption text-grey-6">
              Initiatives added for this performance measure will appear here.
            </div>
          </div>
        </div>
      </q-card-section>

      <q-card-actions align="right" class="pme-initiative-list-actions q-pa-md">
        <q-btn flat label="Close" color="grey-7" @click="close" />
      </q-card-actions>
    </q-card>

    <DeleteConfirmDialog v-model="showDeleteDialog" @confirmDelete="confirmDelete">
      Are you sure you want to delete this initiative?
    </DeleteConfirmDialog>

    <RevertConfirmDialog v-model="showRevertDialog" @confirmRevert="confirmRevert">
      Are you sure you want to revert this accomplishment?
    </RevertConfirmDialog>

    <q-dialog v-model="showHistoryDialog">
      <q-card class="pme-history-dialog rounded-lg shadow-8">
        <!-- HISTORY HEADER -->
        <q-card-section class="row items-center no-wrap q-pa-md">
          <div class="pme-initiative-header-icon">
            <History :size="20" :stroke-width="2.2" />
          </div>
          <div class="min-w-0 q-ml-md col">
            <div class="text-h6 text-weight-bold leading-snug">Initiative History</div>
            <div class="text-caption text-blue-grey-6 pme-break-anywhere">
              {{ selectedHistoryInitiative?.description }}
            </div>
          </div>
          <q-btn flat round dense icon="close" color="grey-7" class="flex-none" v-close-popup>
            <q-tooltip>Close</q-tooltip>
          </q-btn>
        </q-card-section>

        <q-separator />

        <q-card-section class="pme-initiative-list-body q-pa-md">
          <div class="pme-initiative-list-panel bg-white rounded-lg">
            <q-markup-table v-if="selectedHistory.length" flat class="pme-history-table">
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
                  <td class="pme-history-evidence-cell">
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

            <div v-else class="column items-center text-center q-pa-xl">
              <History :size="36" :stroke-width="1.8" class="text-grey-5" />
              <div class="text-weight-medium text-grey-8 q-mt-sm">No evidence history found</div>
              <div class="text-caption text-grey-6">
                Evidence uploaded for this initiative will appear here.
              </div>
            </div>
          </div>
        </q-card-section>

        <q-card-actions align="right" class="pme-initiative-list-actions q-pa-md">
          <q-btn flat label="Close" color="grey-7" v-close-popup />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-dialog>
</template>

<script setup>
import { ref } from 'vue'
import DeleteConfirmDialog from 'src/components/DeleteConfirmDialog.vue'
import RevertConfirmDialog from 'src/components/RevertConfirmDialog.vue'
import {
  Check,
  FileCheck2,
  ClipboardCheck,
  History,
  ListChecks,
  RotateCcw,
  SquarePen,
  Trash2,
  X,
} from 'lucide-vue-next'

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

const props = defineProps({
  modelValue: Boolean,
  indicator: { type: Object, default: () => ({}) },
  initiatives: { type: Array, default: () => [] },
  canChangeInitiative: { type: Boolean, default: true },
  canDeleteInitiative: { type: Boolean, default: true },
  canSubmitAccomplishment: { type: Boolean, default: true },
  canRevertAccomplishment: { type: Boolean, default: true },
})

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

const actionPermission = (row) =>
  row?.is_accomplished ? props.canRevertAccomplishment : props.canSubmitAccomplishment

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

