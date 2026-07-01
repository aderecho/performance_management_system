<template>
  <div class="q-pa-md">
    <PageComboHeader
      title="Role Management"
      :breadcrumbs="[
        { label: 'Home', to: '/admin/dashboard' },
        { label: 'Admin' },
        { label: 'Role Management' },
      ]"
      :buttons="buttons"
      :show-filter="false"
    />

    <AppTable
      title="List of Roles"
      :rows="roleStore.roles"
      :columns="columns"
      row-key="id"
      title-font-size="15px"
      search-width="280px"
      table-header-class="bg-surface text-white"
      @view="handleView"
      @edit="handleEdit"
      @delete="handleStatusToggle"
    >
      <template #body-cell-permission_count="props">
        <q-td :props="props">
          <q-chip color="blue-1" text-color="blue-9" class="text-weight-medium">
            {{ props.row.permission_count || 0 }}
          </q-chip>
        </q-td>
      </template>

      <template #body-cell-is_deleted="props">
        <q-td :props="props">
          <q-chip
            :color="props.row.is_deleted ? 'red-1' : 'green-1'"
            :text-color="props.row.is_deleted ? 'red-9' : 'green-9'"
            class="q-px-md text-weight-medium status-badge"
          >
            <span class="status-dot" :class="props.row.is_deleted ? 'bg-red-9' : 'bg-green-9'" />
            {{ props.row.is_deleted ? 'Inactive' : 'Active' }}
          </q-chip>
        </q-td>
      </template>

      <template #body-cell-actions="props">
        <div class="row items-center justify-center">
          <q-btn size="sm" flat round color="dark-grey" @click="handleView(props.row)">
            <Eye :size="18" :stroke-width="2" />
            <q-tooltip>View</q-tooltip>
          </q-btn>

          <q-btn
            v-if="canChangeRole"
            size="sm"
            flat
            round
            color="secondary"
            @click="handleEdit(props.row)"
          >
            <SquarePen :size="18" :stroke-width="2" />
            <q-tooltip>Edit</q-tooltip>
          </q-btn>

          <q-btn
            v-if="canDeleteRole"
            size="sm"
            flat
            round
            :color="props.row.is_deleted ? 'positive' : 'negative'"
            @click="handleStatusToggle(props.row)"
          >
            <ShieldCheck v-if="props.row.is_deleted" :size="18" :stroke-width="2" />
            <ShieldOff v-else :size="18" :stroke-width="2" />
            <q-tooltip>{{ props.row.is_deleted ? 'Activate' : 'Inactivate' }}</q-tooltip>
          </q-btn>
        </div>
      </template>
    </AppTable>

    <!-- CREATE / UPDATE ROLE -->
    <q-dialog v-model="showFormDialog">
      <q-card class="role-dialog" style="width: 760px; max-width: 94vw">
        <q-card-section class="row items-center no-wrap q-gutter-sm">
          <div class="role-dialog__icon">
            <ShieldCheck :size="20" :stroke-width="2" />
          </div>
          <div class="col">
            <div class="text-h6 leading-snug">
              {{ selectedRole ? 'Update Role' : 'Create Role' }}
            </div>
            <div class="text-caption text-grey-7">
              Assign permissions by toggling them on or off, grouped by module or page.
            </div>
          </div>
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>

        <q-separator />

        <q-form @submit.prevent="handleSubmit">
          <q-card-section class="q-gutter-md">
            <q-input
              v-model="form.name"
              label="Role Name"
              dense
              outlined
              :rules="[(val) => !!val || 'Role name is required']"
              hide-bottom-space
            />

            <!-- Permission toolbar -->
            <div class="perm-toolbar row items-center gap-2">
              <q-btn-toggle
                v-model="groupMode"
                :options="groupModeOptions"
                unelevated
                no-caps
                class="rounded-md"
                toggle-color="primary"
                color="grey-2"
                text-color="grey-8"
              />

              <q-input
                v-model="formSearch"
                dense
                outlined
                clearable
                placeholder="Search permissions"
                class="col"
              >
                <template #prepend>
                  <Search :size="16" :stroke-width="2" class="text-grey-6" />
                </template>
              </q-input>
            </div>

            <div class="row items-center q-gutter-sm justify-between q-mb-sm">
              <div>
                <q-btn
                  flat
                  no-caps
                  size="md"
                  color="primary"
                  icon="done_all"
                  label="Select all"
                  @click="selectAllVisible"
                />
                <q-btn
                  flat
                  no-caps
                  size="md"
                  color="grey-8"
                  icon="remove_done"
                  label="Clear all"
                  @click="clearAllVisible"
                />
              </div>

              <q-chip text-color="primary" class="text-weight-medium">
                {{ selectedCount }} / {{ totalCount }} selected
              </q-chip>
            </div>

            <!-- Grouped permission toggles -->
            <div class="perm-scroll">
              <div v-for="group in formGroups" :key="group.key" class="perm-group q-mb-md">
                <div class="perm-group__header row items-center no-wrap">
                  <component :is="groupIcon" :size="16" :stroke-width="2" class="text-primary" />
                  <div class="col text-weight-semibold q-ml-sm">{{ group.label }}</div>
                  <q-chip dense square color="grey-2" text-color="grey-8" class="q-mr-sm">
                    {{ groupSelectedCount(group) }} / {{ group.permissions.length }}
                  </q-chip>
                  <q-toggle
                    :model-value="groupAllSelected(group)"
                    color="primary"
                    :aria-label="`Toggle all ${group.label} permissions`"
                    @update:model-value="(val) => toggleGroup(group, val)"
                  />
                </div>

                <div class="perm-group__body row q-col-gutter-sm">
                  <div
                    v-for="permission in group.permissions"
                    :key="permission.id"
                    class="col-12 col-sm-6"
                  >
                    <div
                      class="perm-row row items-center no-wrap cursor-pointer"
                      :class="{ 'perm-row--active': isSelected(permission.id) }"
                      @click="setPermission(permission.id, !isSelected(permission.id))"
                    >
                      <div class="col min-w-0">
                        <div class="perm-name ellipsis">{{ permission.name }}</div>
                      </div>
                      <q-toggle
                        :model-value="isSelected(permission.id)"
                        color="primary"
                        :aria-label="permission.name"
                        @update:model-value="(val) => setPermission(permission.id, val)"
                        @click.stop
                      />
                    </div>
                  </div>
                </div>
              </div>

              <div
                v-if="!formGroups.length"
                class="perm-empty column items-center justify-center text-grey-6"
              >
                <SearchX :size="28" :stroke-width="1.5" />
                <div class="q-mt-sm text-caption">No permissions match your search.</div>
              </div>
            </div>
          </q-card-section>

          <q-separator />

          <q-card-actions align="right">
            <q-btn flat label="Cancel" v-close-popup />
            <q-btn
              type="submit"
              color="primary"
              :label="selectedRole ? 'Update' : 'Create'"
              :loading="roleStore.loading.save"
            />
          </q-card-actions>
        </q-form>
      </q-card>
    </q-dialog>

    <!-- VIEW ROLE DETAILS -->
    <ViewDialog
      v-model="showViewDialog"
      :icon="ShieldCheck"
      :title="selectedRole?.name"
      :subtitle="`${viewTotalCount} permission${viewTotalCount === 1 ? '' : 's'} assigned`"
      width="760px"
    >
      <div class="q-gutter-md">
        <div class="perm-toolbar row items-center gap-2">
          <q-btn-toggle
            v-model="groupMode"
            :options="groupModeOptions"
            unelevated
            no-caps
            class="rounded-md"
            toggle-color="primary"
            color="grey-2"
            text-color="grey-8"
          />

          <q-input
            v-model="viewSearch"
            dense
            outlined
            clearable
            placeholder="Search permissions"
            class="col"
          >
            <template #prepend>
              <Search :size="16" :stroke-width="2" class="text-grey-6" />
            </template>
          </q-input>
        </div>

        <div class="perm-scroll">
          <div v-for="group in viewGroups" :key="group.key" class="perm-group">
            <div class="perm-group__header row items-center no-wrap">
              <component :is="groupIcon" :size="16" :stroke-width="2" class="text-primary" />
              <div class="col text-weight-semibold q-ml-sm">{{ group.label }}</div>
              <q-chip dense square color="grey-2" text-color="grey-8">
                {{ group.permissions.length }}
              </q-chip>
            </div>

            <div class="perm-group__body row q-col-gutter-sm">
              <div
                v-for="permission in group.permissions"
                :key="permission.id"
                class="col-12 col-sm-6"
              >
                <div class="perm-row perm-row--readonly row items-center no-wrap">
                  <div class="perm-check">
                    <Check :size="13" :stroke-width="3" />
                  </div>
                  <div class="col min-w-0 q-ml-sm">
                    <div class="perm-name ellipsis">{{ permission.name }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div
            v-if="!viewGroups.length"
            class="perm-empty column items-center justify-center text-grey-6"
          >
            <ShieldOff :size="28" :stroke-width="1.5" />
            <div class="q-mt-sm text-caption">
              {{
                viewTotalCount
                  ? 'No permissions match your search.'
                  : 'No permissions assigned to this role.'
              }}
            </div>
          </div>
        </div>
      </div>
    </ViewDialog>

    <DeleteConfirmDialog
      v-model="showDeleteDialog"
      :loading="roleStore.loading.status"
      :title="selectedRole?.is_deleted ? 'Confirm Activation' : 'Confirm Inactivation'"
      :confirm-label="selectedRole?.is_deleted ? 'Activate' : 'Inactivate'"
      :confirm-color="selectedRole?.is_deleted ? 'positive' : 'negative'"
      @confirmDelete="confirmToggleStatus"
    >
      Are you sure you want to {{ selectedRole?.is_deleted ? 'activate' : 'inactivate' }}
      <strong>{{ selectedRole?.name || 'this role' }}</strong
      >?
    </DeleteConfirmDialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import PageComboHeader from 'src/components/PageComboHeader.vue'
import AppTable from 'src/components/admin/MarkupTable.vue'
import ViewDialog from 'src/components/admin/ViewDialog.vue'
import DeleteConfirmDialog from 'src/components/DeleteConfirmDialog.vue'
import { useAuthStore } from 'src/stores/auth'
import { usePermissionStore } from 'src/stores/permission'
import { useRoleStore } from 'src/stores/role'
import { notify } from 'src/utils/notify'
import {
  Check,
  Eye,
  FileText,
  Search,
  SearchX,
  ShieldCheck,
  ShieldOff,
  SquarePen,
} from 'lucide-vue-next'

const authStore = useAuthStore()
const roleStore = useRoleStore()
const permissionStore = usePermissionStore()

const selectedRole = ref(null)
const showFormDialog = ref(false)
const showViewDialog = ref(false)
const showDeleteDialog = ref(false)

const groupMode = ref('module')
const formSearch = ref('')
const viewSearch = ref('')

const form = reactive({
  name: '',
  permissions: [],
})

const canCreateRole = computed(() =>
  authStore.canAccess({ requiredPermission: 'auth.add_group' }),
)
const canChangeRole = computed(() =>
  authStore.canAccess({ requiredPermission: 'auth.change_group' }),
)
const canDeleteRole = computed(() =>
  authStore.canAccess({ requiredPermission: 'auth.delete_group' }),
)
const canManageRolePermissions = computed(() => canCreateRole.value || canChangeRole.value)

const groupModeOptions = [
  { label: 'By Module', value: 'module', icon: 'widgets' },
  { label: 'By Page', value: 'page', icon: 'description' },
]

const columns = [
  { name: 'name', label: 'Role Name', field: 'name', align: 'left' },
  {
    name: 'permission_count',
    label: 'Permissions',
    field: 'permission_count',
    align: 'center',
  },
  { name: 'is_deleted', label: 'Status', field: 'is_deleted', align: 'center' },
  { name: 'actions', label: 'Actions', field: 'actions', align: 'center' },
]

const buttons = [
  {
    icon: 'add',
    label: 'Add new Role',
    color: 'primary',
    onClick: handleCreate,
    tooltip: 'Create new Role',
    permission: () => canCreateRole.value,
  },
]

const groupIcon = computed(() => (groupMode.value === 'module' ? ShieldCheck : FileText))

const totalCount = computed(() => permissionStore.permissions.length)
const selectedCount = computed(() => form.permissions.length)
const viewTotalCount = computed(() => selectedRole.value?.permission_details?.length || 0)

const formGroups = computed(() =>
  groupPermissions(permissionStore.permissions, groupMode.value, formSearch.value),
)

const viewGroups = computed(() =>
  groupPermissions(selectedRole.value?.permission_details || [], groupMode.value, viewSearch.value),
)

const visibleFormIds = computed(() =>
  formGroups.value.flatMap((group) => group.permissions.map((permission) => permission.id)),
)

function formatGroupName(key) {
  if (!key) return 'Other'
  return key.replace(/[_-]+/g, ' ').replace(/\b\w/g, (char) => char.toUpperCase())
}

function groupPermissions(list, mode, search = '') {
  const field = mode === 'module' ? 'app_label' : 'model'
  const needle = search.trim().toLowerCase()
  const groups = new Map()

  for (const permission of list) {
    if (needle) {
      const haystack =
        `${permission.name} ${permission.permission} ${permission.codename}`.toLowerCase()
      if (!haystack.includes(needle)) continue
    }

    const key = permission[field] || 'other'
    if (!groups.has(key)) groups.set(key, [])
    groups.get(key).push(permission)
  }

  return [...groups.entries()]
    .map(([key, permissions]) => ({
      key,
      label: formatGroupName(key),
      permissions: permissions.slice().sort((a, b) => a.name.localeCompare(b.name)),
    }))
    .sort((a, b) => a.label.localeCompare(b.label))
}

function isSelected(id) {
  return form.permissions.includes(id)
}

function setPermission(id, value) {
  const has = form.permissions.includes(id)
  if (value && !has) {
    form.permissions = [...form.permissions, id]
  } else if (!value && has) {
    form.permissions = form.permissions.filter((permissionId) => permissionId !== id)
  }
}

function groupSelectedCount(group) {
  return group.permissions.reduce(
    (count, permission) => count + (isSelected(permission.id) ? 1 : 0),
    0,
  )
}

function groupAllSelected(group) {
  return (
    group.permissions.length > 0 &&
    group.permissions.every((permission) => isSelected(permission.id))
  )
}

function toggleGroup(group, value) {
  const ids = new Set(form.permissions)
  for (const permission of group.permissions) {
    if (value) ids.add(permission.id)
    else ids.delete(permission.id)
  }
  form.permissions = [...ids]
}

function selectAllVisible() {
  const ids = new Set(form.permissions)
  for (const id of visibleFormIds.value) ids.add(id)
  form.permissions = [...ids]
}

function clearAllVisible() {
  const visible = new Set(visibleFormIds.value)
  form.permissions = form.permissions.filter((id) => !visible.has(id))
}

function resetForm() {
  form.name = ''
  form.permissions = []
}

function setForm(role) {
  form.name = role?.name || ''
  form.permissions = role?.permission_details?.map((permission) => permission.id) || []
}

function handleCreate() {
  selectedRole.value = null
  resetForm()
  formSearch.value = ''
  showFormDialog.value = true
}

function handleView(row) {
  selectedRole.value = row
  viewSearch.value = ''
  showViewDialog.value = true
}

function handleEdit(row) {
  selectedRole.value = row
  setForm(row)
  formSearch.value = ''
  showFormDialog.value = true
}

function handleStatusToggle(row) {
  selectedRole.value = row
  showDeleteDialog.value = true
}

async function handleSubmit() {
  if (!form.name) {
    notify.negative('Role name is required.')
    return
  }

  try {
    const payload = {
      name: form.name,
      permissions: form.permissions,
    }

    if (selectedRole.value?.id) {
      await roleStore.updateRole(selectedRole.value.id, payload)
      notify.positive('Role updated successfully.')
    } else {
      await roleStore.createRole(payload)
      notify.positive('Role created successfully.')
    }

    showFormDialog.value = false
    selectedRole.value = null
    resetForm()
  } catch (err) {
    console.error('Save role failed:', err)
    notify.negative('Failed to save role. Please try again.')
  }
}

async function confirmToggleStatus() {
  if (!selectedRole.value?.id) return

  try {
    const wasInactive = selectedRole.value.is_deleted

    if (wasInactive) {
      await roleStore.setRoleActive(selectedRole.value.id)
      notify.positive('Role activated successfully.')
    } else {
      await roleStore.setRoleInactive(selectedRole.value.id)
      notify.positive('Role inactivated successfully.')
    }

    showDeleteDialog.value = false
    selectedRole.value = null
  } catch (err) {
    console.error('Update role status failed:', err)
    notify.negative('Failed to update role status. Please try again.')
  }
}

onMounted(async () => {
  try {
    const requests = [roleStore.fetchRoles()]
    if (canManageRolePermissions.value) {
      requests.push(permissionStore.fetchPermissions())
    }
    await Promise.all(requests)
  } catch {
    notify.negative('Failed to load role management data. Please try again.')
  }
})
</script>
