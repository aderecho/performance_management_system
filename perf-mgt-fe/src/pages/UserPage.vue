<template>
    <div class="q-pa-md">

        <PageComboHeader title="User Management" :breadcrumbs="[
            { label: 'Home', to: '/' },
            { label: 'Admin' },
            { label: 'User Management' }
        ]" :buttons="buttons" />

        <!-- CARDS -->
        <div class="row q-col-gutter-md q-mb-md">

            <div class="col-12 col-sm-6 col-md-4">
                <DashboardCard title="Total Users" :value="userStore.stats?.total_users.value" icon="people"
                    :trend="userStore.stats?.total_users.trend + '% vs last month'" />
            </div>

            <div class="col-12 col-sm-6 col-md-4">
                <DashboardCard title="Active Users" :value="userStore.stats?.active_users.value" icon="groups"
                    :trend="userStore.stats?.active_users.trend + '% vs last month'" />
            </div>

            <div class="col-12 col-sm-6 col-md-4">
                <DashboardCard title="New Users" :value="userStore.stats?.new_users.value" icon="person_add"
                    :trend="userStore.stats?.new_users.trend + '% vs last month'" />
            </div>

        </div>

        <AppTable title="Users" :rows="userStore.users" :columns="columns" row-key="email" @view="handleView"
            @edit="handleEdit" @delete="handleDelete" />

        <ViewDialog v-model="showViewDialog" title="User Details" :data="selectedUser" :fields="userFields" />

        <FormDialog v-model="showFormDialog" title="User" :data="selectedUser" :loading="userStore.loading"
            @submit="handleSubmit" />
    </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import PageComboHeader from 'src/components/PageComboHeader.vue'
import DashboardCard from 'src/components/admin/DashboardCard.vue'
import ViewDialog from 'src/components/admin/ViewDialog.vue'
import FormDialog from 'src/components/admin/FormDialog.vue'
import AppTable from 'src/components/admin/MarkupTable.vue'
import { useUserStore } from 'src/stores/user'

const userStore = useUserStore()
const showViewDialog = ref(false)
const selectedUser = ref(null)
const showFormDialog = ref(false)

const columns = [
    { name: 'name', label: 'Name', field: row => row.profile.last_name + ', ' + row.profile.first_name, align: 'left' },
    { name: 'email', label: 'Email', field: 'email', align: 'center' },
    { name: 'primary_unit', label: 'Primary Unit', field: row => row.primary_unit, align: 'center' },
    { name: 'is_active', label: 'Status', field: 'is_active', align: 'center' },
    { name: 'is_superuser', label: 'Super User', field: 'is_superuser', align: 'center' },
    { name: 'actions', label: 'Actions', field: 'actions', align: 'center' }
]

// View
function handleView(row) {
    console.log('View:', row)
    selectedUser.value = row
    showViewDialog.value = true
}

const userFields = [
    { label: 'Email', key: 'email' },

    {
        label: 'Full Name',
        key: 'profile',
        format: (_, data) => {
            const p = data.profile || {}
            return p.last_name && p.first_name ? `${p.last_name}, ${p.first_name} ${p.middle_name || ''}` : '-'
        }
    },

    {
        label: 'Status',
        key: 'is_active',
        type: 'badge',
        badge: (val) => ({
            label: val ? 'Active' : 'Suspended',
            color: val ? 'positive' : 'negative'
        })
    },

    {
        label: 'Superuser',
        key: 'is_superuser',
        type: 'badge',
        badge: (val) => ({
            label: val ? 'Yes' : 'No',
            color: val ? 'positive' : 'negative'
        })
    },

    {
        label: 'Primary Unit',
        key: 'primary_unit'
    },

    {
        label: 'Date Created',
        key: 'created_at',
        format: (val) => new Date(val).toLocaleString()
    },

    {
        label: 'Date Last Updated',
        key: 'updated_at',
        format: (val) => new Date(val).toLocaleString()
    }
]

function handleEdit(row) {
    console.log('Edit:', row.id)
    selectedUser.value = row
    showFormDialog.value = true
}

function handleDelete(row) {
    console.log('Delete:', row)
}

async function handleSubmit(formData) {
    console.log('Form submitted:', formData)

    try {
        const payload = {
            email: formData.email,
            is_active: formData.is_active,
            is_superuser: formData.is_superuser,

            profile: {
                first_name: formData.profile.first_name,
                middle_name: formData.profile.middle_name,
                last_name: formData.profile.last_name,
                suffix: formData.profile.suffix
            },

            // Transform units into user_units
            user_units: formData.units.map(unitId => ({
                unit: unitId,
                is_primary: unitId === formData.primary_unit
            }))
        }

        await userStore.createUser(payload)

        showFormDialog.value = false

        await userStore.fetchUsers()

    } catch (err) {
        console.error('Create user failed:', err)
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
        tooltip: 'Create new User'
    },
]

onMounted(() => {
    userStore.fetchUsers()
    userStore.fetchUserStats()
})
</script>