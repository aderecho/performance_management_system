<template>
  <div class="q-pa-md">
    <PageComboHeader
      title="Permission Management"
      :breadcrumbs="[
        { label: 'Home', to: '/admin/dashboard' },
        { label: 'Admin' },
        { label: 'Permission Management' },
      ]"
      :show-filter="false"
    />

    <AppTable
      title="User Permissions"
      :rows="userStore.users"
      :columns="columns"
      row-key="id"
      title-font-size="15px"
      search-width="280px"
      table-header-class="bg-surface text-white"
    >
      <template #body-cell-name="props">
        <q-td :props="props">
          {{ formatUserName(props.row) }}
        </q-td>
      </template>

      <template #body-cell-permission_count="props">
        <q-td :props="props">
          <q-chip color="blue-1" text-color="blue-9" class="text-weight-medium">
            {{ props.row.permission_count || 0 }}
          </q-chip>
        </q-td>
      </template>

      <template #body-cell-direct_permissions="props">
        <q-td :props="props">
          <q-chip color="teal-1" text-color="teal-9" class="text-weight-medium">
            {{ props.row.direct_permission_ids?.length || 0 }}
          </q-chip>
        </q-td>
      </template>


      <!-- ACTIONS -->
      <template #body-cell-actions="props">
        <div class="row full-width items-center justify-center no-wrap">
          <q-btn size="sm" flat round color="dark-grey" @click="handleView(props.row)">
            <Eye :size="18" :stroke-width="2" />
            <q-tooltip>View Permissions</q-tooltip>
          </q-btn>

          <q-btn size="sm" flat round color="secondary" @click="handleEdit(props.row)">
            <UserCog :size="18" :stroke-width="2" />
            <q-tooltip>Edit Permissions</q-tooltip>
          </q-btn>
        </div>
      </template>
    </AppTable>

    <q-dialog v-model="showViewDialog">
      <q-card class="dialog-form">
        <q-card-section class="row items-center justify-between">
          <div class="text-h6">User Permissions</div>
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>

        <q-separator />

        <q-card-section>
          <div class="text-subtitle2">{{ formatUserName(selectedUser) }}</div>
          <div class="text-caption text-grey-7 q-mb-md">{{ selectedUser?.email }}</div>

          <div class="text-weight-medium q-mb-sm">Direct Permissions</div>
          <div class="row q-col-gutter-sm q-mb-md">
            <div
              v-for="permission in selectedUser?.direct_permission_details || []"
              :key="permission.id"
              class="col-12 col-sm-6"
            >
              <q-chip color="teal-1" text-color="teal-9" class="full-width">
                {{ permission.permission }}
              </q-chip>
            </div>
            <div v-if="!selectedUser?.direct_permission_details?.length" class="col-12 text-grey-7">
              No direct permissions assigned.
            </div>
          </div>

          <div class="text-weight-medium q-mb-sm">Effective Permissions</div>
          <div class="row q-col-gutter-sm">
            <div
              v-for="permission in selectedUser?.effective_permissions || []"
              :key="permission"
              class="col-12 col-sm-6"
            >
              <q-chip color="blue-1" text-color="blue-9" class="full-width">
                {{ permission }}
              </q-chip>
            </div>
            <div v-if="!selectedUser?.effective_permissions?.length" class="col-12 text-grey-7">
              No effective permissions assigned.
            </div>
          </div>
        </q-card-section>
      </q-card>
    </q-dialog>

    <q-dialog v-model="showEditDialog">
      <q-card class="dialog-form">
        <q-card-section class="row items-center justify-between">
          <div class="text-h6">Edit Permissions</div>
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>

        <q-separator />

        <q-card-section>
          <div class="text-subtitle2">{{ formatUserName(selectedUser) }}</div>
          <div class="text-caption text-grey-7 q-mb-md">{{ selectedUser?.email }}</div>

          <q-select
            v-model="permissionForm.permissionIds"
            v-model:input-value="permissionSearch"
            :options="filteredPermissionOptions"
            option-value="value"
            option-label="label"
            emit-value
            map-options
            multiple
            use-chips
            use-input
            input-debounce="250"
            label="Direct Permissions"
            outlined
            dense
            @filter="filterPermissions"
            @update:model-value="permissionSearch = ''"
          />
        </q-card-section>

        <q-separator />

        <q-card-actions align="right">
          <q-btn flat label="Cancel" v-close-popup />
          <q-btn
            color="primary"
            label="Update"
            :loading="userStore.loading.save"
            @click="handleSubmit"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import PageComboHeader from 'src/components/PageComboHeader.vue'
import AppTable from 'src/components/admin/MarkupTable.vue'
import { usePermissionStore } from 'src/stores/permission'
import { useUserStore } from 'src/stores/user'
import { Eye, UserCog } from 'lucide-vue-next'
import { notify } from 'src/utils/notify'

const permissionStore = usePermissionStore()
const userStore = useUserStore()

const selectedUser = ref(null)
const showViewDialog = ref(false)
const showEditDialog = ref(false)
const permissionSearch = ref('')
const filteredPermissionOptions = ref([])
const permissionForm = reactive({
  permissionIds: [],
})

const columns = [
  { name: 'name', label: 'Full Name', field: row => formatUserName(row), align: 'left' },
  { name: 'email', label: 'Email', field: 'email', align: 'left' },
  { name: 'roles', label: 'Roles', field: row => row.roles?.join(', ') || '-', align: 'left' },
  {
    name: 'direct_permissions',
    label: 'Direct',
    field: row => row.direct_permission_ids?.length || 0,
    align: 'center',
  },
  {
    name: 'permission_count',
    label: 'Effective',
    field: 'permission_count',
    align: 'center',
  },
  { name: 'actions', label: 'Actions', field: 'actions', align: 'center' },
]

const permissionOptions = computed(() => permissionStore.permissions.map((permission) => ({
  label: `${permission.permission} - ${permission.name}`,
  value: permission.id,
})))

function formatUserName(user) {
  const profile = user?.profile || {}
  const fullName = [profile.last_name, profile.first_name].filter(Boolean).join(', ')
  return fullName || user?.email || '-'
}

function filterPermissions(value, update) {
  update(() => {
    const needle = value.toLowerCase()
    filteredPermissionOptions.value = permissionOptions.value.filter((permission) => (
      permission.label.toLowerCase().includes(needle)
    ))
  })
}

function handleView(row) {
  selectedUser.value = row
  showViewDialog.value = true
}

function handleEdit(row) {
  selectedUser.value = row
  permissionForm.permissionIds = [...(row.direct_permission_ids || [])]
  filteredPermissionOptions.value = permissionOptions.value
  showEditDialog.value = true
}

async function handleSubmit() {
  if (!selectedUser.value?.id) return

  try {
    const updatedUser = await userStore.updateUserPermissions(
      selectedUser.value.id,
      permissionForm.permissionIds,
    )
    selectedUser.value = updatedUser
    showEditDialog.value = false
    notify.positive('User permissions updated successfully.')
  } catch (err) {
    console.error('Update user permissions failed:', err)
    notify.negative('Failed to update user permissions. Please try again.')
  }
}

onMounted(async () => {
  try {
    await Promise.all([
      userStore.fetchUsers(),
      permissionStore.fetchPermissions(),
    ])
    filteredPermissionOptions.value = permissionOptions.value
  } catch {
    notify.negative('Failed to load user permissions. Please try again.')
  }
})
</script>
