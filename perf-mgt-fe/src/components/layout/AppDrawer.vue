<template>
    <q-drawer :model-value="modelValue" @update:model-value="$emit('update:modelValue', $event)" show-if-above bordered
        class="text-dark column no-wrap" :width="300">
        <q-scroll-area class="col">
            <q-list class="text-dark q-pa-md q-gutter-y-sm">
                <!-- ADMIN LINKS-->
                <div v-if="authStore.isSuperAdmin">
                    <q-item v-for="link in links" :key="link.text" clickable :to="link.to" class="rounded"
                        active-class="bg-grey text-primary">
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

        <!-- Footer -->
        <div class="q-pa-md">
            <div class="flex flex-center q-gutter-xs">
                <a class="text-primary" href="https://privacy.up.edu.ph" target="_blank">
                    Privacy Policy
                </a>
                <span> · </span>
                <a class="text-primary" href="javascript:void(0)">
                    About the App
                </a>
            </div>
        </div>
    </q-drawer>
</template>

<script setup>
import { onMounted } from 'vue'
import { usePmeTemplateStore } from 'src/stores/pme/template'
import { documentRoute } from 'src/router/routeHelpers'
import { useAuthStore } from 'src/stores/auth'
import { Gauge, UsersRound, ShieldUser, FileClock, KeyRound, ScrollText } from 'lucide-vue-next'
import { notify } from 'src/utils/notify'

const authStore = useAuthStore()

defineProps({
    modelValue: {
        type: Boolean,
        required: true
    }
})

defineEmits(['update:modelValue'])

const pmeTemplateStore = usePmeTemplateStore()

const links = [
    { icon: Gauge, text: 'Dashboard', to: '/dashboard' },
    { icon: UsersRound, text: 'User Management', to: '/admin/users' },
    { icon: ShieldUser, text: 'Role Management', to: '/admin/roles' },
    { icon: KeyRound, text: 'Permission Management', to: '/admin/permissions' },
    { icon: FileClock, text: 'Audit Logs', to: '/admin/audit-logs' },
]

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
