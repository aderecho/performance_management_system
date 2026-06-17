<template>
    <q-drawer :model-value="modelValue" @update:model-value="$emit('update:modelValue', $event)" show-if-above bordered
        class="text-primary" :width="280">
        <q-scroll-area class="fit">
            <q-list class="text-primary q-pt-sm">
                <q-item clickable to="/dashboard">
                    <q-item-section avatar>
                        <q-icon name="dashboard" />
                    </q-item-section>
                    <q-item-section>
                        <q-item-label>Dashboard</q-item-label>
                    </q-item-section>
                </q-item>
            </q-list>

            <q-separator v-if="configStore.templateList?.length" inset class="q-my-sm" />

            <q-list class="text-primary">
                <q-expansion-item v-for="template in configStore.templateList" :key="template.id" icon="description"
                    :label="template.name" dense-toggle>
                    <q-item v-for="document in template.documents" :key="document.id" clickable
                        :to="documentRoute(document.id)">
                        <q-item-section>
                            <q-item-label>{{ document.name }}</q-item-label>
                        </q-item-section>
                    </q-item>
                </q-expansion-item>

                <q-separator v-if="configStore.templateList?.length" inset class="q-my-sm" />

                <!-- Admin links -->
                <div v-if="authStore.isSuperAdmin">
                    <q-item v-for="link in adminLinks" :key="link.text" clickable :to="link.to">
                        <q-item-section avatar>
                            <q-icon :name="link.icon" />
                        </q-item-section>
                        <q-item-section>
                            <q-item-label>{{ link.text }}</q-item-label>
                        </q-item-section>
                    </q-item>
                </div>

                <!-- Footer -->
                <div class="q-mt-md">
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

            </q-list>
        </q-scroll-area>
    </q-drawer>
</template>

<script setup>
import { onMounted } from 'vue'
import { useConfigStore } from 'src/stores/config'
import { documentRoute } from 'src/router/routeHelpers'
import { useAuthStore } from 'src/stores/auth'

const authStore = useAuthStore()

defineProps({
    modelValue: {
        type: Boolean,
        required: true
    }
})

defineEmits(['update:modelValue'])

const configStore = useConfigStore()

const adminLinks = [
    { icon: 'person', text: 'User Management', to: '/admin/users' },
    { icon: 'groups', text: 'Role Management', to: '/admin/roles' },
    { icon: 'admin_panel_settings', text: 'Permission Management', to: '/admin/permissions' },
    { icon: 'list', text: 'Audit Logs', to: '/admin/audit-logs' },
]

onMounted(async () => {
    // preserve original behavior
    if (!configStore.templateList?.length) {
        try {
            await configStore.getTemplateList()
        } catch {
            // Store captures the error state.
        }
    }
})
</script>
