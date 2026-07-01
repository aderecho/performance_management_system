<template>
    <q-drawer :model-value="modelValue" @update:model-value="$emit('update:modelValue', $event)" show-if-above bordered
        :mini="miniState" class="text-dark column no-wrap" :width="300">
        <!-- OPEN OR CLOSE TOGGLE -->
        <div class="row items-center q-px-sm q-pt-sm" :class="miniState ? 'justify-center' : 'justify-end'">
            <q-btn flat dense round color="dark-grey"
                :aria-label="miniState ? 'Expand navigation drawer' : 'Collapse navigation drawer'"
                @click="toggleDrawer">
                <PanelLeftOpen v-if="miniState" :size="22" :stroke-width="2" />
                <PanelLeftClose v-else :size="22" :stroke-width="2" />
                <q-tooltip>{{ miniState ? 'Expand menu' : 'Collapse menu' }}</q-tooltip>
            </q-btn>
        </div>

        <!-- LOGO  -->
        <transition name="drawer-collapse">
            <div v-if="!miniState" class="flex flex-center q-px-md q-pb-sm">
                <img :src="UPCLOGO" alt="UPlan360 logo" class="drawer-logo" />
            </div>
        </transition>

        <q-scroll-area class="col">
            <q-list padding class="text-dark q-gutter-y-sm q-px-md">
                <!-- ADMIN LINKS-->
                <div v-if="visibleLinks.length">
                    <q-item v-for="link in visibleLinks" :key="link.text" clickable :to="link.to" class="rounded"
                        active-class="bg-primary text-white text-weight-medium">
                        <q-item-section avatar>
                            <component :is="link.icon" :size="22" :stroke-width="2" />
                        </q-item-section>
                        <q-item-section>
                            <q-item-label>{{ link.text }}</q-item-label>
                        </q-item-section>
                    </q-item>
                </div>

                <q-separator v-if="pmeTemplateStore.templates?.length" inset class="q-my-sm" />

                <!-- DOCUMENTS -->
                <q-expansion-item v-for="template in pmeTemplateStore.templates" :key="template.id" dense-toggle>
                    <template #header>
                        <q-item-section avatar>
                            <ScrollText :size="22" :stroke-width="2" />
                        </q-item-section>
                        <q-item-section>
                            <q-item-label>{{ template.name }}</q-item-label>
                        </q-item-section>
                    </template>
                    <q-item v-for="document in template.documents" :key="document.id" clickable
                        :to="documentRoute(document.id)">
                        <q-item-section>
                            <q-item-label>{{ document.name }}</q-item-label>
                        </q-item-section>
                    </q-item>
                </q-expansion-item>
            </q-list>
        </q-scroll-area>

        <!-- FOOTER-->
        <transition name="drawer-collapse">
            <div v-if="!miniState" class="q-pa-md">
                <div class="flex flex-center q-gutter-lg">
                    <a class="text-primary" href="https://privacy.up.edu.ph" target="_blank">
                        Privacy Policy
                    </a>

                    <a class="text-primary" href="javascript:void(0)">
                        About the App
                    </a>
                </div>
            </div>
        </transition>
    </q-drawer>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useQuasar } from 'quasar'
import { usePmeTemplateStore } from 'src/stores/pme/template'
import { documentRoute } from 'src/router/routeHelpers'
import { PAGE_ACCESS } from 'src/router/pageAccess'
import { useAuthStore } from 'src/stores/auth'
import { Gauge, 
         UsersRound, 
         ShieldUser, 
         FileClock, 
         KeyRound, 
         ScrollText, 
         PanelLeftClose, 
         PanelLeftOpen 
        } from 'lucide-vue-next'
import { notify } from 'src/utils/notify'
import UPCLOGO from 'assets/UPCLOGO.png'

const $q = useQuasar()
const authStore = useAuthStore()

defineProps({
    modelValue: {
        type: Boolean,
        required: true
    }
})

const emit = defineEmits(['update:modelValue'])

// Collapsed (mini) state shows only icons on desktop. On mobile the drawer
// uses overlay mode (mini is ignored), so the toggle closes it instead.
const miniState = ref(false)

function toggleDrawer() {
    if ($q.screen.lt.md) {
        emit('update:modelValue', false)
    } else {
        miniState.value = !miniState.value
    }
}

const pmeTemplateStore = usePmeTemplateStore()

const links = [
    { icon: Gauge, text: 'Dashboard', to: '/admin/dashboard', meta: PAGE_ACCESS.dashboard },
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
]

const visibleLinks = computed(() => {
    return links.filter((link) => !link.meta || authStore.canAccess(link.meta))
})

onMounted(async () => {
    // preserve original behavior
    if (!pmeTemplateStore.templates?.length) {
        try {
            await pmeTemplateStore.fetchTemplates()
        } catch {
            notify.negative('Failed to load PME documents. Please try again.')
        }
    }
})
</script>
