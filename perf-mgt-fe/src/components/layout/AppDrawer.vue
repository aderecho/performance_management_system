<template>
    <q-drawer :model-value="modelValue" @update:model-value="$emit('update:modelValue', $event)" show-if-above bordered
        :mini="miniState" class="bg-surface text-dark column no-wrap" :width="300">
        <!-- OPEN OR CLOSE TOGGLE -->
        <!-- <div class="row items-center q-px-sm q-pt-sm" :class="miniState ? 'justify-center' : 'justify-end'">
            <q-btn flat dense round color="dark-grey"
                :aria-label="miniState ? 'Expand navigation drawer' : 'Collapse navigation drawer'"
                @click="toggleDrawer">
                <PanelLeftOpen v-if="miniState" :size="22" :stroke-width="2" />
                <PanelLeftClose v-else :size="22" :stroke-width="2" />
                <q-tooltip>{{ miniState ? 'Expand menu' : 'Collapse menu' }}</q-tooltip>
            </q-btn>
        </div> -->

        <!-- LOGO  -->
        <transition name="drawer-collapse">
            <div v-if="!miniState" class="flex flex-center q-pa-md q-pb-sm">
                <img :src="UPCLOGO" alt="UPlan360 logo" class="drawer-logo" />
            </div>
        </transition>

        <q-scroll-area class="col">
            <q-list padding class="text-grey q-gutter-y-sm q-px-md">
                <!-- DASHBOARDS -->
                <q-expansion-item v-if="canAccessDashboard" dense-toggle>
                    <template #header>
                        <q-item-section avatar>
                            <Gauge :size="22" :stroke-width="2" />
                        </q-item-section>
                        <q-item-section>
                            <q-item-label>Executive Dashboard</q-item-label>
                        </q-item-section>
                    </template>
                    <q-item clickable :to="{ name: 'dashboard' }" class="rounded"
                        active-class="bg-white text-black text-weight-medium">
                        <q-item-section>
                            <q-item-label>Performance Dashboard</q-item-label>
                        </q-item-section>
                    </q-item>
                    <q-item v-for="dashboard in dashboardEmbedStore.dashboards" :key="dashboard.slug" clickable
                        :to="{ name: 'embedded-dashboard', params: { dashboardSlug: dashboard.slug } }" class="rounded"
                        active-class="bg-white text-black text-weight-medium">
                        <q-item-section>
                            <q-item-label>{{ dashboard.name }}</q-item-label>
                        </q-item-section>
                    </q-item>
                </q-expansion-item>

                <!-- ADMIN LINKS-->
                <div v-if="visibleLinks.length">
                    <q-item v-for="link in visibleLinks" :key="link.text" clickable :to="link.to" class="rounded"
                        active-class="bg-white text-black text-weight-medium">
                        <q-item-section avatar>
                            <component :is="link.icon" :size="22" :stroke-width="2" />
                        </q-item-section>
                        <q-item-section>
                            <q-item-label>{{ link.text }}</q-item-label>
                        </q-item-section>
                    </q-item>
                </div>

                <!-- ARCHIVED -->
                <q-expansion-item v-if="canAccessArchived" dense-toggle>
                    <template #header>
                        <q-item-section avatar>
                            <FolderArchive :size="22" :stroke-width="2" />
                        </q-item-section>
                        <q-item-section>
                            <q-item-label>Archived</q-item-label>
                        </q-item-section>
                    </template>
                    <q-item clickable :to="{ name: 'archived-initiatives' }" class="rounded"
                        active-class="bg-white text-black text-weight-medium">
                        <q-item-section>
                            <q-item-label>Initiative</q-item-label>
                        </q-item-section>
                    </q-item>
                </q-expansion-item>

            </q-list>
        </q-scroll-area>

        <!-- FOOTER-->
        <transition name="drawer-collapse">
            <div v-if="!miniState" class="q-pa-md">
                <q-separator class="q-mb-md drawer-footer-divider" />
                <div class="column q-gutter-sm">
                    <a class="drawer-footer-link" href="https://privacy.up.edu.ph" target="_blank"
                        rel="noopener noreferrer">
                        <ShieldCheck :size="18" :stroke-width="2" />
                        <span>Privacy Policy</span>
                    </a>

                    <a class="drawer-footer-link" href="https://support.upcebu.edu.ph/open.php?topicId=63"
                        target="_blank" rel="noopener noreferrer">
                        <Headset :size="18" :stroke-width="2" />
                        <span>ITC Support</span>
                    </a>
                </div>
            </div>
        </transition>
    </q-drawer>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
// import { useQuasar } from 'quasar'
import { PAGE_ACCESS } from 'src/router/pageAccess'
import { useAuthStore } from 'src/stores/auth'
import { useDashboardEmbedStore } from 'src/stores/dashboardEmbed'
import {
    Gauge,
    UsersRound,
    ShieldUser,
    FileClock,
    KeyRound,
    FileStack,
    FolderArchive,
    Settings,
    ShieldCheck,
    Headset,
} from 'lucide-vue-next'
import UPCLOGO from 'assets/UPCLOGO.png'

// const $q = useQuasar()
const authStore = useAuthStore()
const dashboardEmbedStore = useDashboardEmbedStore()

defineProps({
    modelValue: {
        type: Boolean,
        required: true
    }
})

// const emit = defineEmits(['update:modelValue'])

// Collapsed (mini) state shows only icons on desktop. On mobile the drawer
// uses overlay mode (mini is ignored), so the toggle closes it instead.
const miniState = ref(false)

// function toggleDrawer() {
//     if ($q.screen.lt.md) {
//         emit('update:modelValue', false)
//     } else {
//         miniState.value = !miniState.value
//     }
// }

const links = [
    {
        icon: FileStack,
        text: 'Documents',
        to: '/documents',
        meta: PAGE_ACCESS.documents,
    },
    {
        icon: UsersRound,
        text: 'User Management',
        to: '/admin/users',
        meta: PAGE_ACCESS.users,
    },
    {
        icon: ShieldUser,
        text: 'Role Management',
        to: '/admin/roles',
        meta: PAGE_ACCESS.roles,
    },
    {
        icon: KeyRound,
        text: 'Permission Management',
        to: '/admin/permissions',
        meta: PAGE_ACCESS.permissions,
    },
    {
        icon: FileClock,
        text: 'Audit Logs',
        to: '/admin/audit-logs',
        meta: PAGE_ACCESS.auditLogs,
    },
    {
        icon: Settings,
        text: 'Settings',
        to: '/admin/settings',
        meta: PAGE_ACCESS.settings,
    },
]

const visibleLinks = computed(() => {
    return links.filter((link) => !link.meta || authStore.canAccess(link.meta))
})

const canAccessDashboard = computed(() => authStore.canAccess(PAGE_ACCESS.dashboard))
const canAccessArchived = computed(() => authStore.canAccess(PAGE_ACCESS.archivedInitiatives))

onMounted(() => {
    if (canAccessDashboard.value) {
        dashboardEmbedStore.fetchDashboards().catch(() => { })
    }
})
</script>
