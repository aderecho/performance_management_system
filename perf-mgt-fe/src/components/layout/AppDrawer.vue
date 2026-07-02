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
import { computed, ref } from 'vue'
// import { useQuasar } from 'quasar'
import { PAGE_ACCESS } from 'src/router/pageAccess'
import { useAuthStore } from 'src/stores/auth'
import { Gauge,
         UsersRound,
         ShieldUser,
         FileClock,
         KeyRound,
         FileStack,
         FolderArchive,
         ShieldCheck,
         Headset,
        } from 'lucide-vue-next'
import UPCLOGO from 'assets/UPCLOGO.png'

// const $q = useQuasar()
const authStore = useAuthStore()

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
    { icon: Gauge, text: 'Executive Dashboard', to: '/admin/dashboard', meta: PAGE_ACCESS.dashboard },
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
        icon: FileStack,
        text: 'Documents',
        to: '/documents',
        meta: PAGE_ACCESS.documents,
    },
]

const visibleLinks = computed(() => {
    return links.filter((link) => !link.meta || authStore.canAccess(link.meta))
})

const canAccessArchived = computed(() => authStore.canAccess(PAGE_ACCESS.archivedInitiatives))
</script>

<style scoped>
.drawer-footer-divider {
    background: rgba(255, 255, 255, 0.15);
}

.drawer-footer-link {
    align-items: center;
    border-radius: 10px;
    color: rgba(255, 255, 255, 0.75);
    display: flex;
    font-size: 0.8125rem;
    font-weight: 500;
    gap: 10px;
    padding: 8px 12px;
    text-decoration: none;
    transition: background-color 0.2s ease, color 0.2s ease;
}

.drawer-footer-link:hover {
    background: rgba(255, 255, 255, 0.12);
    color: #ffffff;
}

.drawer-footer-link:focus-visible {
    outline: 2px solid rgba(255, 255, 255, 0.7);
    outline-offset: 2px;
}
</style>
