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
      @delete="handleDelete"
    >
      <template #body-cell-permission_count="props">
        <q-td :props="props">
          <q-chip color="blue-1" text-color="blue-9" class="text-weight-medium">
            {{ props.row.permission_count || 0 }}
          </q-chip>
        </q-td>
      </template>
    </AppTable>

    <q-dialog v-model="showFormDialog">
      <q-card class="dialog-form">
        <q-card-section class="row items-center justify-between">
          <div class="text-h6">{{ selectedRole ? 'Update Role' : 'Create Role' }}</div>
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>

        <q-separator />

        <q-card-section>
          <q-form @submit.prevent="handleSubmit">
            <div class="row q-col-gutter-md">
              <div class="col-12">
                <q-input
                  v-model="form.name"
                  label="Role Name"
                  dense
                  outlined
                  :rules="[(val) => !!val || 'Required']"
                  hide-bottom-space
                />
              </div>

              <div class="col-12">
                <q-select
                  v-model="form.permissions"
                  :options="permissionOptions"
                  option-value="value"
                  option-label="label"
                  emit-value
                  map-options
                  multiple
                  use-chips
                  label="Permissions"
                  outlined
                  dense
                />
              </div>
            </div>
          </q-form>
        </q-card-section>

        <q-separator />

        <q-card-actions align="right">
          <q-btn flat label="Cancel" v-close-popup />
          <q-btn
            color="primary"
            :label="selectedRole ? 'Update' : 'Create'"
            :loading="roleStore.loading.save"
            @click="handleSubmit"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <q-dialog v-model="showViewDialog">
      <q-card class="dialog-form">
        <q-card-section class="row items-center justify-between">
          <div class="text-h6">Role Details</div>
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>

        <q-separator />

        <q-card-section>
          <div class="text-subtitle2 q-mb-sm">{{ selectedRole?.name }}</div>
          <div class="row q-col-gutter-sm">
            <div
              v-for="permission in selectedRole?.permission_details || []"
              :key="permission.id"
              class="col-12 col-sm-6"
            >
              <q-chip color="grey-2" text-color="dark" class="full-width">
                {{ permission.permission }}
              </q-chip>
            </div>
          </div>
        </q-card-section>
      </q-card>
    </q-dialog>

    <DeleteConfirmDialog
      v-model="showDeleteDialog"
      :loading="roleStore.loading.delete"
      @confirmDelete="confirmDelete"
    >
      Are you sure you want to delete
      <strong>{{ selectedRole?.name || 'this role' }}</strong>?
    </DeleteConfirmDialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import PageComboHeader from 'src/components/PageComboHeader.vue'
import AppTable from 'src/components/admin/MarkupTable.vue'
import DeleteConfirmDialog from 'src/components/DeleteConfirmDialog.vue'
import { usePermissionStore } from 'src/stores/permission'
import { useRoleStore } from 'src/stores/role'
import { notify } from 'src/utils/notify'

const roleStore = useRoleStore()
const permissionStore = usePermissionStore()

const selectedRole = ref(null)
const showFormDialog = ref(false)
const showViewDialog = ref(false)
const showDeleteDialog = ref(false)

const form = reactive({
  name: '',
  permissions: [],
})

const columns = [
  { name: 'name', label: 'Role Name', field: 'name', align: 'left' },
  {
    name: 'permission_count',
    label: 'Permissions',
    field: 'permission_count',
    align: 'center',
  },
  { name: 'actions', label: 'Actions', field: 'actions', align: 'center' },
]

const permissionOptions = computed(() => permissionStore.permissions.map((permission) => ({
  label: `${permission.permission} - ${permission.name}`,
  value: permission.id,
})))

const buttons = [
  {
    icon: 'add',
    label: 'Add new Role',
    color: 'primary',
    onClick: handleCreate,
    tooltip: 'Create new Role',
  },
]

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
  showFormDialog.value = true
}

function handleView(row) {
  selectedRole.value = row
  showViewDialog.value = true
}

function handleEdit(row) {
  selectedRole.value = row
  setForm(row)
  showFormDialog.value = true
}

function handleDelete(row) {
  selectedRole.value = row
  showDeleteDialog.value = true
}

async function handleSubmit() {
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

async function confirmDelete() {
  if (!selectedRole.value?.id) return

  try {
    await roleStore.deleteRole(selectedRole.value.id)
    notify.positive('Role deleted successfully.')
    showDeleteDialog.value = false
    selectedRole.value = null
  } catch (err) {
    console.error('Delete role failed:', err)
    notify.negative('Failed to delete role. Please try again.')
  }
}

onMounted(async () => {
  try {
    await Promise.all([
      roleStore.fetchRoles(),
      permissionStore.fetchPermissions(),
    ])
  } catch {
    notify.negative('Failed to load role management data. Please try again.')
  }
})
</script>
