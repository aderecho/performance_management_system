<template>
  <div class="q-pa-md">
    <PageComboHeader
      title="User Management"
      :breadcrumbs="[
        { label: 'Home', to: '/admin/dashboard' },
        { label: 'Admin' },
        { label: 'User Management' },
      ]"
      :buttons="buttons"
      :show-filter="false"
    />

    <!-- CARDS -->
    <div class="row q-col-gutter-md q-mb-md">
      <div class="col-12 col-sm-6 col-md">
        <DashboardCard
          title="Total Users"
          :value="userStore.stats?.total_users.value"
          :icon="Users"
          :icon-size="26"
          icon-bg-class="bg-soft-blue"
          icon-color="blue-8"
          :trend="userStore.stats?.total_users.trend + '% vs last month'"
        />
      </div>

      <div class="col-12 col-sm-6 col-md">
        <DashboardCard
          title="New Users"
          :value="userStore.stats?.new_users.value"
          :icon="UserPlus"
          :icon-size="26"
          icon-bg-class="bg-soft-purple"
          icon-color="blue-8"
          :trend="userStore.stats?.new_users.trend + '% vs last month'"
        />
      </div>

      <div class="col-12 col-sm-6 col-md">
        <DashboardCard
          title="Active Users"
          :value="userStore.stats?.active_users.value"
          :icon="UserCheck"
          :icon-size="26"
          icon-bg-class="bg-soft-green"
          icon-color="green-8"
          :trend="userStore.stats?.active_users.trend + '% vs last month'"
        />
      </div>

      <div class="col-12 col-sm-6 col-md">
        <DashboardCard
          title="Active Staff"
          :value="userStore.stats?.active_staff.value"
          :icon="UserCog"
          :icon-size="26"
          icon-bg-class="bg-soft-purple"
          icon-color="purple-8"
          :trend="userStore.stats?.active_staff.trend + '% vs last month'"
        />
      </div>

      <div class="col-12 col-sm-6 col-md">
        <DashboardCard
          title="Active Admin"
          :value="userStore.stats?.active_admin.value"
          :icon="ShieldUser"
          :icon-size="26"
          icon-bg-class="bg-soft-blue"
          icon-color="blue-8"
          :trend="userStore.stats?.active_admin.trend + '% vs last month'"
        />
      </div>
    </div>

    <AppTable
      ref="userTable"
      title="List of Users"
      :rows="filteredUsers"
      :columns="columns"
      row-key="email"
      title-font-size="15px"
      search-width="280px"
      table-header-class="bg-surface text-white"
      @view="handleView"
      @edit="handleEdit"
      @delete="handleDelete"
    >
      <template #filters>
        <UserFilters v-model="filters" @change="handleFilter" />
      </template>

      <template #body-cell-roles="props">
        <q-td :props="props">
          <div class="row items-center gap-2">
            <q-chip
              v-for="role in roleStore.roleNamesByIds(props.row.role_ids)"
              :key="role"
              color="blue-1"
              text-color="blue-9"
              class="text-weight-medium"
              dense
            >
              {{ role }}
            </q-chip>
            <span v-if="!roleStore.roleNamesByIds(props.row.role_ids).length">-</span>
          </div>
        </q-td>
      </template>

      <template #body-cell-actions="props">
        <div class="row items-center justify-center">
          <q-btn size="sm" flat round color="dark-grey" @click="handleView(props.row)">
            <Eye :size="18" :stroke-width="2" />
            <q-tooltip>View</q-tooltip>
          </q-btn>

          <q-btn size="sm" flat round color="secondary" @click="handleEdit(props.row)">
            <SquarePen :size="18" :stroke-width="2" />
            <q-tooltip>Edit</q-tooltip>
          </q-btn>

          <q-btn
            size="sm"
            flat
            round
            :color="props.row.is_active ? 'negative' : 'positive'"
            @click="handleDelete(props.row)"
          >
            <UserRoundCheck v-if="!props.row.is_active" :size="18" :stroke-width="2" />
            <UserRoundX v-else :size="18" :stroke-width="2" />
            <q-tooltip>{{ props.row.is_active ? 'Deactivate' : 'Activate' }}</q-tooltip>
          </q-btn>
        </div>
      </template>
    </AppTable>

    <ViewDialog
      v-model="showViewDialog"
      :icon="UserRound"
      :title="selectedUser ? fullName : 'User Details'"
      :subtitle="selectedUser?.email"
      width="560px"
    >
      <UserDetailsView :data="selectedUser" />
    </ViewDialog>

    <FormDialog
      v-model="showFormDialog"
      title="User"
      :data="selectedUser"
      :loading="userStore.loading.save"
      @submit="handleSubmit"
    />

    <DeleteConfirmDialog
      v-model="showDeleteDialog"
      :loading="userStore.loading.delete"
      :title="selectedUser?.is_active ? 'Confirm Deactivation' : 'Confirm Activation'"
      :confirm-label="selectedUser?.is_active ? 'Deactivate' : 'Activate'"
      :confirm-color="selectedUser?.is_active ? 'negative' : 'positive'"
      @confirmDelete="confirmToggleStatus"
    >
      Are you sure you want to {{ selectedUser?.is_active ? 'deactivate' : 'activate' }}
      <strong>{{ selectedUser?.email || 'this user' }}</strong
      >?
    </DeleteConfirmDialog>
  </div>
</template>
<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import PageComboHeader from 'src/components/PageComboHeader.vue'
import DashboardCard from 'src/components/admin/DashboardCard.vue'
import ViewDialog from 'src/components/admin/ViewDialog.vue'
import UserDetailsView from 'src/components/admin/UserDetailsView.vue'
import FormDialog from 'src/components/admin/FormDialog.vue'
import UserFilters from 'src/components/admin/UserFilters.vue'
import AppTable from 'src/components/admin/MarkupTable.vue'
import DeleteConfirmDialog from 'src/components/DeleteConfirmDialog.vue'
import { useUserStore } from 'src/stores/user'
import { useRoleStore } from 'src/stores/role'
import {
  Eye,
  SquarePen,
  UserRound,
  UserRoundX,
  UserRoundCheck,
  ShieldUser,
  UserCog,
  Users,
  UserCheck,
  UserPlus,
} from 'lucide-vue-next'
import { notify } from 'src/utils/notify'

const userStore = useUserStore()
const roleStore = useRoleStore()
const showViewDialog = ref(false)
const selectedUser = ref(null)
const showFormDialog = ref(false)
const showDeleteDialog = ref(false)
const userTable = ref(null)
const filters = ref({
  primary_unit: null,
  is_active: null,
  is_superuser: null,
})

const fullName = computed(() => {
  const p = selectedUser.value?.profile || {}
  const first = p.first_name?.trim() || ''
  const last = p.last_name?.trim() || ''
  const middle = p.middle_name?.trim() || ''
  const suffix = p.suffix?.trim() || ''

  if (!first && !last) return 'Unnamed user'

  const middleInitial = middle ? ` ${middle.charAt(0)}.` : ''
  const suffixPart = suffix ? `, ${suffix}` : ''
  const base = last ? `${last}, ${first}${middleInitial}` : `${first}${middleInitial}`
  return `${base}${suffixPart}`
})

const columns = [
  {
    name: 'name',
    label: 'Full Name',
    field: (row) => row.profile.last_name + ', ' + row.profile.first_name,
    align: 'left',
  },
  { name: 'email', label: 'Email', field: 'email', align: 'left' },
  { name: 'primary_unit', label: 'Primary Unit', field: (row) => row.primary_unit, align: 'left' },
  {
    name: 'roles',
    label: 'Roles',
    field: (row) => roleStore.roleNamesByIds(row.role_ids).join(', ') || '-',
    align: 'left',
  },
  { name: 'is_active', label: 'Status', field: 'is_active', align: 'center' },
  { name: 'is_superuser', label: 'Super User', field: 'is_superuser', align: 'center' },
  { name: 'actions', label: 'Actions', field: 'actions', align: 'center' },
]

const filteredUsers = computed(() =>
  userStore.users.filter((user) => {
    const primaryUnit = filters.value.primary_unit
    const isActive = filters.value.is_active
    const isSuperuser = filters.value.is_superuser

    if (primaryUnit) {
      const hasPrimaryUnit = user.user_units?.some(
        (userUnit) =>
          userUnit.unit === primaryUnit && userUnit.is_primary && userUnit.is_active,
      )

      if (!hasPrimaryUnit) return false
    }

    if (isActive !== null && isActive !== undefined && isActive !== '') {
      if (user.is_active !== (isActive === 'true')) return false
    }

    if (isSuperuser !== null && isSuperuser !== undefined && isSuperuser !== '') {
      if (user.is_superuser !== (isSuperuser === 'true')) return false
    }

    return true
  }),
)

// View
function handleView(row) {
  console.log('View:', row)
  selectedUser.value = row
  showViewDialog.value = true
}

function handleEdit(row) {
  console.log('Edit:', row.id)
  selectedUser.value = row
  showFormDialog.value = true
}

function handleDelete(row) {
  console.log('Delete:', row)
  selectedUser.value = row
  showDeleteDialog.value = true
}

async function loadUsers() {
  await userStore.fetchUsers()
}

async function handleFilter(nextFilters) {
  filters.value = { ...nextFilters }
  await nextTick()
  userTable.value?.resetPagination()
}

async function confirmToggleStatus() {
  if (!selectedUser.value?.id) return

  const wasActive = selectedUser.value.is_active
  const actionPast = wasActive ? 'deactivated' : 'activated'
  const actionVerb = wasActive ? 'deactivate' : 'activate'

  try {
    if (wasActive) {
      await userStore.deactivateUser(selectedUser.value.id)
    } else {
      await userStore.activateUser(selectedUser.value.id)
    }
    notify.positive(`User ${actionPast} successfully.`)

    showDeleteDialog.value = false
    selectedUser.value = null

    await loadUsers()
    await userStore.fetchUserStats()
  } catch (err) {
    console.error(`Failed to ${actionVerb} user:`, err)
    notify.negative(`Failed to ${actionVerb} user. Please try again.`)
  }
}

async function handleSubmit(formData) {
  console.log('Form submitted:', formData)
  const isEdit = !!selectedUser.value?.id

  try {
    const payload = {
      email: formData.email,
      is_active: formData.is_active,
      is_superuser: formData.is_superuser,
      role_ids: formData.role_ids,

      profile: {
        first_name: formData.profile.first_name,
        middle_name: formData.profile.middle_name,
        last_name: formData.profile.last_name,
        suffix: formData.profile.suffix,
      },

      // Transform units into user_units
      user_units: formData.units.map((unitId) => ({
        unit: unitId,
        is_primary: unitId === formData.primary_unit,
      })),
    }

    if (!isEdit || formData.password) {
      payload.password = formData.password
    }

    if (isEdit) {
      await userStore.updateUser(selectedUser.value.id, payload)
      notify.positive('User updated successfully.')
    } else {
      await userStore.createUser(payload)
      notify.positive('User created successfully.')
    }

    showFormDialog.value = false

    await loadUsers()
    await userStore.fetchUserStats()

    if (!isEdit) {
      await nextTick()
      userTable.value?.resetPagination()
    }
  } catch (err) {
    console.error(`${isEdit ? 'Update' : 'Create'} user failed:`, err)
    console.log('Form submitted:', formData)
    notify.negative(`Failed to ${isEdit ? 'update' : 'create'} user. Please try again.`)
  }
}

// Create
function handleCreate() {
  console.log('Create new user')
  selectedUser.value = null
  showFormDialog.value = true
}

const buttons = [
  {
    icon: 'add',
    label: 'Add new User',
    color: 'primary',
    onClick: handleCreate,
    tooltip: 'Create new User',
  },
]

onMounted(async () => {
  try {
    await Promise.all([loadUsers(), roleStore.fetchRoles()])
  } catch {
    notify.negative('Failed to load users. Please try again.')
  }

  try {
    await userStore.fetchUserStats()
  } catch {
    notify.negative('Failed to load user stats. Please try again.')
  }
})
</script>
