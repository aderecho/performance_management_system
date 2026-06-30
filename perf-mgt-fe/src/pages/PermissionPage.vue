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
      :rows="filteredUsers"
      :columns="columns"
      row-key="id"
      title-font-size="15px"
      search-width="280px"
      table-header-class="bg-surface text-white"
    >
      <template #filters>
        <q-select
          v-model="userTypeFilter"
          :options="userTypeOptions"
          option-label="label"
          option-value="value"
          emit-value
          map-options
          outlined
          dense
          clearable
          label="Type"
          class="rounded-2xl permission-type-filter flex-none"
        />
      </template>

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

    <!-- VIEW USER PERMISSIONS -->
    <ViewDialog
      v-model="showViewDialog"
      :icon="ShieldCheck"
      :title="formatUserName(selectedUser)"
      :subtitle="selectedUser?.email"
      width="720px"
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

        <q-tabs
          v-model="viewTab"
          dense
          no-caps
          align="left"
          active-color="primary"
          indicator-color="primary"
          class="text-grey-7"
        >
          <q-tab name="direct" :label="`Direct (${directCount})`" />
          <q-tab name="effective" :label="`Effective (${effectiveCount})`" />
        </q-tabs>

        <q-separator />

        <q-tab-panels v-model="viewTab" animated class="permission-tab-panels">
          <q-tab-panel name="direct" class="q-pa-none q-pt-md">
            <div class="perm-scroll">
              <div v-for="group in directGroups" :key="group.key" class="perm-group q-mb-md">
                <div class="perm-group__header row items-center no-wrap">
                  <component :is="groupIcon" :size="16" :stroke-width="2" class="text-primary" />
                  <div class="col text-weight-semibold q-ml-sm">{{ group.label }}</div>
                  <q-chip dense square color="teal-1" text-color="teal-9">
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
                        <!-- <div
                            v-if="
                              permission.permission && permission.permission !== permission.name
                            "
                            class="perm-code text-grey-6 ellipsis"
                          >
                            {{ permission.permission }}
                          </div> -->
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div
                v-if="!directGroups.length"
                class="perm-empty column items-center justify-center text-grey-6"
              >
                <ShieldOff :size="28" :stroke-width="1.5" />
                <div class="q-mt-sm text-caption">
                  {{
                    directCount
                      ? 'No permissions match your search.'
                      : 'No direct permissions assigned.'
                  }}
                </div>
              </div>
            </div>
          </q-tab-panel>

          <q-tab-panel name="effective" class="q-pa-none q-pt-md">
            <div class="perm-scroll">
              <div v-for="group in effectiveGroups" :key="group.key" class="perm-group q-mb-md">
                <div class="perm-group__header row items-center no-wrap">
                  <component :is="groupIcon" :size="16" :stroke-width="2" class="text-primary" />
                  <div class="col text-weight-semibold q-ml-sm">{{ group.label }}</div>
                  <q-chip dense square color="blue-1" text-color="blue-9">
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
                      <div class="perm-check perm-check--blue">
                        <Check :size="13" :stroke-width="3" />
                      </div>
                      <div class="col min-w-0 q-ml-sm">
                        <div class="perm-name ellipsis">{{ permission.name }}</div>
                        <!-- <div
                            v-if="
                              permission.permission && permission.permission !== permission.name
                            "
                            class="perm-code text-grey-6 ellipsis"
                          >
                            {{ permission.permission }}
                          </div> -->
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div
                v-if="!effectiveGroups.length"
                class="perm-empty column items-center justify-center text-grey-6"
              >
                <ShieldOff :size="28" :stroke-width="1.5" />
                <div class="q-mt-sm text-caption">
                  {{
                    effectiveCount
                      ? 'No permissions match your search.'
                      : 'No effective permissions assigned.'
                  }}
                </div>
              </div>
            </div>
          </q-tab-panel>
        </q-tab-panels>
      </div>
    </ViewDialog>

    <!-- EDIT DIRECT PERMISSIONS -->
    <q-dialog v-model="showEditDialog">
      <q-card class="permission-dialog">
        <q-card-section class="row items-center no-wrap q-gutter-sm">
          <div class="permission-dialog__icon">
            <UserCog :size="20" :stroke-width="2" />
          </div>
          <div class="col min-w-0">
            <div class="text-h6 leading-snug ellipsis">Edit Direct Permissions</div>
            <div class="text-caption text-grey-7 ellipsis">
              {{ formatUserName(selectedUser) }} | {{ selectedUser?.email }}
            </div>
          </div>
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>

        <q-separator />

        <q-card-section class="q-gutter-md">
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
              v-model="editSearch"
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

          <div class="row items-center justify-between q-gutter-sm">
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

          <div class="perm-scroll">
            <div v-for="group in editGroups" :key="group.key" class="perm-group q-mb-md">
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
                      <div class="perm-code text-grey-6 ellipsis">{{ permission.permission }}</div>
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
              v-if="!editGroups.length"
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
import ViewDialog from 'src/components/admin/ViewDialog.vue'
import { usePermissionStore } from 'src/stores/permission'
import { useUserStore } from 'src/stores/user'
import { useRoleStore } from 'src/stores/role'
import {
  Eye,
  UserCog,
  ShieldCheck,
  ShieldOff,
  FileText,
  Search,
  SearchX,
  Check,
} from 'lucide-vue-next'
import { notify } from 'src/utils/notify'

const permissionStore = usePermissionStore()
const userStore = useUserStore()
const roleStore = useRoleStore()

const selectedUser = ref(null)
const showViewDialog = ref(false)
const showEditDialog = ref(false)

const groupMode = ref('module')
const viewTab = ref('direct')
const viewSearch = ref('')
const editSearch = ref('')

// null = all, true = admin (superuser), false = staff (non-superuser)
const userTypeFilter = ref(null)
const userTypeOptions = [
  { label: 'Admin', value: true },
  { label: 'Staff', value: false },
]

const filteredUsers = computed(() => {
  if (userTypeFilter.value === null) return userStore.users
  return userStore.users.filter((user) => !!user.is_superuser === userTypeFilter.value)
})

const permissionForm = reactive({
  permissionIds: [],
})

const groupModeOptions = [
  { label: 'By Module', value: 'module', icon: 'widgets' },
  { label: 'By Page', value: 'page', icon: 'description' },
]

const columns = [
  { name: 'name', label: 'Full Name', field: (row) => formatUserName(row), align: 'left' },
  { name: 'email', label: 'Email', field: 'email', align: 'left' },
  {
    name: 'roles',
    label: 'Roles',
    field: (row) => roleStore.roleNamesByIds(row.role_ids).join(', ') || '-',
    align: 'left',
  },
  {
    name: 'direct_permissions',
    label: 'Direct',
    field: (row) => row.direct_permission_ids?.length || 0,
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

const groupIcon = computed(() => (groupMode.value === 'module' ? ShieldCheck : FileText))

const totalCount = computed(() => permissionStore.permissions.length)
const selectedCount = computed(() => permissionForm.permissionIds.length)
const directPermissions = computed(() =>
  permissionStore.permissionsByIds(selectedUser.value?.direct_permission_ids),
)
const directCount = computed(() => directPermissions.value.length)
const effectiveCount = computed(() => selectedUser.value?.effective_permissions?.length || 0)

const permissionByCode = computed(() => {
  const map = new Map()
  for (const permission of permissionStore.permissions) {
    map.set(permission.permission, permission)
  }
  return map
})

function enrichCodes(codes) {
  return codes.map((code) => {
    const found = permissionByCode.value.get(code)
    if (found) return found

    const [appLabel, ...rest] = code.split('.')
    return {
      id: code,
      permission: code,
      name: code,
      codename: rest.join('.'),
      app_label: appLabel || 'other',
      model: 'other',
    }
  })
}

const directGroups = computed(() =>
  groupPermissions(directPermissions.value, groupMode.value, viewSearch.value),
)

const effectiveGroups = computed(() =>
  groupPermissions(
    enrichCodes(selectedUser.value?.effective_permissions || []),
    groupMode.value,
    viewSearch.value,
  ),
)

const editGroups = computed(() =>
  groupPermissions(permissionStore.permissions, groupMode.value, editSearch.value),
)

const visibleEditIds = computed(() =>
  editGroups.value.flatMap((group) => group.permissions.map((permission) => permission.id)),
)

function formatUserName(user) {
  const profile = user?.profile || {}
  const fullName = [profile.last_name, profile.first_name].filter(Boolean).join(', ')
  return fullName || user?.email || '-'
}

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
  return permissionForm.permissionIds.includes(id)
}

function setPermission(id, value) {
  const has = permissionForm.permissionIds.includes(id)
  if (value && !has) {
    permissionForm.permissionIds = [...permissionForm.permissionIds, id]
  } else if (!value && has) {
    permissionForm.permissionIds = permissionForm.permissionIds.filter(
      (permissionId) => permissionId !== id,
    )
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
  const ids = new Set(permissionForm.permissionIds)
  for (const permission of group.permissions) {
    if (value) ids.add(permission.id)
    else ids.delete(permission.id)
  }
  permissionForm.permissionIds = [...ids]
}

function selectAllVisible() {
  const ids = new Set(permissionForm.permissionIds)
  for (const id of visibleEditIds.value) ids.add(id)
  permissionForm.permissionIds = [...ids]
}

function clearAllVisible() {
  const visible = new Set(visibleEditIds.value)
  permissionForm.permissionIds = permissionForm.permissionIds.filter((id) => !visible.has(id))
}

function handleView(row) {
  selectedUser.value = row
  viewSearch.value = ''
  viewTab.value = 'direct'
  showViewDialog.value = true
}

function handleEdit(row) {
  selectedUser.value = row
  permissionForm.permissionIds = [...(row.direct_permission_ids || [])]
  editSearch.value = ''
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
      roleStore.fetchRoles(),
    ])
  } catch {
    notify.negative('Failed to load user permissions. Please try again.')
  }
})
</script>
