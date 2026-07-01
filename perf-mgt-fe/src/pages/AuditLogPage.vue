<template>
  <div class="q-pa-md">
    <PageComboHeader
      title="Audit Logs"
      :breadcrumbs="[
        { label: 'Home', to: '/admin/dashboard' },
        { label: 'Admin' },
        { label: 'Audit Logs' },
      ]"
      :show-filter="false"
    />

    <div v-if="canViewAuditLogs" class="audit-filters row q-col-gutter-sm q-mb-md">
      <div class="col-12 col-sm-6 col-md-2">
        <q-select
          v-model="filters.module"
          class="rounded-2xl"
          :options="moduleOptions"
          label="Module"
          outlined
          dense
          clearable
          emit-value
          map-options
          @update:model-value="loadAuditLogs"
        />
      </div>

      <div class="col-12 col-sm-6 col-md-2">
        <q-select
          v-model="filters.action"
          class="rounded-2xl"
          :options="actionOptions"
          label="Action"
          outlined
          dense
          clearable
          emit-value
          map-options
          @update:model-value="loadAuditLogs"
        />
      </div>

      <div class="col-12 col-sm-6 col-md-2">
        <q-select
          v-model="filters.target_type"
          class="rounded-2xl"
          :options="targetTypeOptions"
          label="Target"
          outlined
          dense
          clearable
          emit-value
          map-options
          @update:model-value="loadAuditLogs"
        />
      </div>

      <div class="col-12 col-sm-6 col-md-2">
        <q-input
          v-model="filters.date_from"
          class="rounded-2xl"
          label="From"
          type="date"
          outlined
          dense
          clearable
          @update:model-value="loadAuditLogs"
        />
      </div>

      <div class="col-12 col-sm-6 col-md-2">
        <q-input
          v-model="filters.date_to"
          class="rounded-2xl"
          label="To"
          type="date"
          outlined
          dense
          clearable
          @update:model-value="loadAuditLogs"
        />
      </div>

      <div class="col-12 col-sm-6 col-md-2">
        <q-input
          v-model="filters.user"
          class="rounded-2xl"
          label="User Email"
          outlined
          dense
          clearable
          debounce="400"
          @update:model-value="loadAuditLogs"
        >
          <template #prepend>
            <q-icon name="search" />
          </template>
        </q-input>
      </div>
    </div>

    <q-banner
      v-if="canViewAuditLogs && auditLogStore.error.list"
      rounded
      class="bg-red-1 text-red-9 q-mb-md"
    >
      Failed to load audit logs. Please try again.
    </q-banner>

    <AppTable
      v-if="canViewAuditLogs"
      title="System Activity"
      :rows="auditLogStore.logs"
      :columns="columns"
      row-key="id"
      title-font-size="15px"
      search-width="280px"
      search-placeholder="Search loaded logs"
      table-header-class="bg-surface text-white"
      @view="handleView"
    >
      <template #filters>
        <q-btn
          flat
          round
          color="primary"
          :loading="auditLogStore.loading.list"
          @click="loadAuditLogs"
        >
          <RefreshCw :size="18" :stroke-width="2" />
          <q-tooltip>Refresh</q-tooltip>
        </q-btn>
      </template>

      <template #body-cell-created_at="props">
        <q-td :props="props">
          <div class="text-weight-medium">{{ formatDateTime(props.row.created_at) }}</div>
        </q-td>
      </template>

      <template #body-cell-module="props">
        <q-td :props="props">
          <q-chip
            dense
            class="text-weight-medium"
            :color="moduleColor(props.row.module).bg"
            :text-color="moduleColor(props.row.module).text"
          >
            {{ moduleLabel(props.row.module) }}
          </q-chip>
        </q-td>
      </template>

      <template #body-cell-action="props">
        <q-td :props="props">
          <q-chip dense color="blue-1" text-color="blue-9" class="text-weight-medium">
            {{ actionLabel(props.row.action) }}
          </q-chip>
        </q-td>
      </template>

      <template #body-cell-target="props">
        <q-td :props="props">
          <div class="text-weight-medium ellipsis">{{ props.row.target_label || '-' }}</div>
          <div class="text-caption text-grey-7">{{ targetTypeLabel(props.row.target_type) }}</div>
        </q-td>
      </template>

      <template #body-cell-summary="props">
        <q-td :props="props">
          <div class="audit-summary">{{ props.row.summary }}</div>
        </q-td>
      </template>

      <template #body-cell-actions="props">
        <div class="row items-center justify-center">
          <q-btn size="sm" flat round color="dark-grey" @click="handleView(props.row)">
            <Eye :size="18" :stroke-width="2" />
            <q-tooltip>View details</q-tooltip>
          </q-btn>
        </div>
      </template>
    </AppTable>

    <q-dialog v-model="showDetails">
      <q-card class="audit-dialog">
        <q-card-section class="row items-center no-wrap q-gutter-sm">
          <div class="audit-dialog__icon">
            <ShieldCheck :size="20" :stroke-width="2" />
          </div>
          <div class="col min-w-0">
            <div class="text-h6 ellipsis">{{ selectedLog?.summary || 'Audit Log Details' }}</div>
            <div class="text-caption text-grey-7">{{ formatDateTime(selectedLog?.created_at) }}</div>
          </div>
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>

        <q-separator />

        <q-card-section v-if="selectedLog" class="q-gutter-md">
          <div class="row q-col-gutter-sm">
            <div
              v-for="item in detailItems"
              :key="item.label"
              class="col-12 col-sm-6"
            >
              <div class="audit-detail">
                <div class="text-caption text-grey-7">{{ item.label }}</div>
                <div class="text-body2 text-weight-medium break-word">{{ item.value || '-' }}</div>
              </div>
            </div>
          </div>

          <div>
            <div class="text-subtitle2 q-mb-sm">Metadata</div>
            <div v-if="metadataEntries.length" class="row q-col-gutter-sm">
              <div
                v-for="entry in metadataEntries"
                :key="entry.key"
                class="col-12 col-sm-6"
              >
                <div class="audit-detail">
                  <div class="text-caption text-grey-7">{{ formatKey(entry.key) }}</div>
                  <div class="text-body2 break-word">{{ formatMetadataValue(entry.value) }}</div>
                </div>
              </div>
            </div>
            <div v-else class="text-grey-7">No metadata recorded.</div>
          </div>
        </q-card-section>
      </q-card>
    </q-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import PageComboHeader from 'src/components/PageComboHeader.vue'
import AppTable from 'src/components/admin/MarkupTable.vue'
import { useAuthStore } from 'src/stores/auth'
import { useAuditLogStore } from 'src/stores/auditLog'
import { notify } from 'src/utils/notify'
import { Eye, RefreshCw, ShieldCheck } from 'lucide-vue-next'

const authStore = useAuthStore()
const auditLogStore = useAuditLogStore()
const selectedLog = ref(null)
const showDetails = ref(false)

const canViewAuditLogs = computed(() =>
  authStore.canAccess({ requiresSuperAdmin: true }),
)

const filters = reactive({
  module: null,
  action: null,
  target_type: null,
  user: '',
  date_from: '',
  date_to: '',
  limit: 200,
})

const moduleOptions = [
  { label: 'Auth', value: 'auth' },
  { label: 'Admin', value: 'admin' },
  { label: 'PME', value: 'pme' },
  { label: 'Core', value: 'core' },
]

const actionOptions = [
  { label: 'Login Success', value: 'login.success' },
  { label: 'Logout Success', value: 'logout.success' },
  { label: 'User Create', value: 'user.create' },
  { label: 'User Update', value: 'user.update' },
  { label: 'User Activate', value: 'user.activate' },
  { label: 'User Deactivate', value: 'user.deactivate' },
  { label: 'Role Create', value: 'role.create' },
  { label: 'Role Update', value: 'role.update' },
  { label: 'Role Activate', value: 'role.activate' },
  { label: 'Role Deactivate', value: 'role.deactivate' },
  { label: 'Role Delete', value: 'role.delete' },
  { label: 'Document Create', value: 'document.create' },
  { label: 'Document Update', value: 'document.update' },
  { label: 'Document Delete', value: 'document.delete' },
  { label: 'Item Create', value: 'item.create' },
  { label: 'Item Update', value: 'item.update' },
  { label: 'Item Delete', value: 'item.delete' },
  { label: 'Initiative Create', value: 'initiative.create' },
  { label: 'Initiative Update', value: 'initiative.update' },
  { label: 'Initiative Delete', value: 'initiative.delete' },
  { label: 'Accomplishment Submit', value: 'accomplishment.submit' },
  { label: 'Accomplishment Update', value: 'accomplishment.update' },
  { label: 'Accomplishment Revert', value: 'accomplishment.revert' },
  { label: 'Evidence Upload', value: 'evidence.upload' },
  { label: 'Evidence Revert', value: 'evidence.revert' },
]

const targetTypeOptions = [
  { label: 'User', value: 'user' },
  { label: 'Role', value: 'role' },
  { label: 'Document', value: 'document' },
  { label: 'Item', value: 'item' },
  { label: 'Initiative', value: 'initiative' },
  { label: 'Accomplishment', value: 'initiativeaccomplishment' },
]

const columns = [
  { name: 'created_at', label: 'Time', field: 'created_at', align: 'left' },
  { name: 'user_full_name', label: 'User', field: 'user_full_name', align: 'left' },
  { name: 'module', label: 'Module', field: 'module', align: 'center' },
  { name: 'action', label: 'Action', field: 'action', align: 'center' },
  { name: 'target', label: 'Target', field: 'target_label', align: 'left' },
  { name: 'summary', label: 'Summary', field: 'summary', align: 'left' },
  { name: 'actions', label: 'Actions', field: 'actions', align: 'center' },
]

const metadataEntries = computed(() =>
  Object.entries(selectedLog.value?.metadata || {}).map(([key, value]) => ({ key, value })),
)

const detailItems = computed(() => [
  { label: 'User Email', value: selectedLog.value?.user_email },
  { label: 'Module', value: moduleLabel(selectedLog.value?.module) },
  { label: 'Action', value: actionLabel(selectedLog.value?.action) },
  { label: 'Target Type', value: targetTypeLabel(selectedLog.value?.target_type) },
  { label: 'Target', value: selectedLog.value?.target_label },
  { label: 'IP Address', value: selectedLog.value?.ip_address },
  { label: 'User Agent', value: selectedLog.value?.user_agent },
])

function moduleLabel(value) {
  return moduleOptions.find((option) => option.value === value)?.label || formatKey(value)
}

function actionLabel(value) {
  return actionOptions.find((option) => option.value === value)?.label || formatKey(value)
}

function targetTypeLabel(value) {
  return targetTypeOptions.find((option) => option.value === value)?.label || formatKey(value)
}

function moduleColor(value) {
  const colors = {
    auth: { bg: 'green-1', text: 'green-9' },
    admin: { bg: 'blue-1', text: 'blue-9' },
    pme: { bg: 'purple-1', text: 'purple-9' },
    core: { bg: 'grey-3', text: 'grey-9' },
  }
  return colors[value] || colors.core
}

function formatKey(value = '') {
  return String(value || '')
    .replace(/[._-]+/g, ' ')
    .replace(/\b\w/g, (char) => char.toUpperCase())
}

function formatDateTime(value) {
  if (!value) return '-'
  return new Date(value).toLocaleString()
}

function formatMetadataValue(value) {
  if (Array.isArray(value)) return value.join(', ')
  if (value && typeof value === 'object') return JSON.stringify(value)
  if (typeof value === 'boolean') return value ? 'Yes' : 'No'
  return value ?? '-'
}

function handleView(row) {
  selectedLog.value = row
  showDetails.value = true
}

async function loadAuditLogs() {
  try {
    await auditLogStore.fetchAuditLogs(filters)
  } catch (err) {
    console.error('Failed to load audit logs:', err)
    notify.negative('Failed to load audit logs. Please try again.')
  }
}

onMounted(() => {
  if (canViewAuditLogs.value) {
    loadAuditLogs()
  }
})
</script>
