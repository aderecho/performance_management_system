<template>
    <div class="row q-col-gutter-sm q-mb-md">
        <div class="col-12 col-md">
            <q-input
                v-model="local.search"
                class="rounded-2xl"
                outlined
                dense
                clearable
                debounce="350"
                placeholder="Search objective or performance measure..."
                @update:model-value="emitChange"
            >
                <template #prepend>
                    <q-icon name="search" />
                </template>
            </q-input>
        </div>

        <div class="col-12 col-md-3">
            <q-select
                v-model="local.sra"
                class="rounded-2xl"
                :options="sraOptions"
                option-label="label"
                option-value="value"
                emit-value
                map-options
                outlined
                dense
                clearable
                label="Strategic Result Area"
                @update:model-value="emitChange"
            />
        </div>

        <div class="col-12 col-md-2">
            <q-select
                v-model="local.status"
                class="rounded-2xl"
                :options="statusOptions"
                option-label="label"
                option-value="value"
                emit-value
                map-options
                outlined
                dense
                clearable
                label="Status"
                @update:model-value="emitChange"
            />
        </div>
    </div>
</template>

<script setup>
import { reactive, watch } from 'vue'

const props = defineProps({
    modelValue: { type: Object, default: () => ({}) },
    sraOptions: { type: Array, default: () => [] },
    statusOptions: { type: Array, default: () => [] }
})

const emit = defineEmits(['update:modelValue', 'change'])

const local = reactive({
    search: '',
    sra: null,
    status: null
})

watch(
    () => props.modelValue,
    value => {
        local.search = value?.search || ''
        local.sra = value?.sra || null
        local.status = value?.status || null
    },
    { immediate: true, deep: true }
)

function emitChange() {
    const filters = {
        search: local.search || null,
        sra: local.sra || null,
        status: local.status || null
    }

    emit('update:modelValue', filters)
    emit('change', filters)
}
</script>
