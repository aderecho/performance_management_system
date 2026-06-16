<template>
    <q-dialog v-model="model">
        <q-card style="min-width: 500px; max-width: 700px; width: 100%">

            <q-card-section class="row items-center justify-between">
                <div class="text-h6">
                    {{ isEdit ? 'Edit User' : 'Create User' }}
                </div>
                <q-btn icon="close" flat round dense v-close-popup />
            </q-card-section>

            <q-separator />

            <!-- FORM -->
            <q-card-section>
                <q-form @submit.prevent="handleSubmit">

                    <div class="row q-col-gutter-md">

                        <div class="col-12">
                            <q-input v-model="form.email" label="Email" type="email" dense outlined
                                :rules="[val => !!val || 'Required']" hide-bottom-space />
                        </div>

                        <div class="col-12 col-sm-6">
                            <q-input v-model="form.profile.first_name" label="First Name" dense outlined
                                :rules="[val => !!val || 'Required']" hide-bottom-space />
                        </div>

                        <div class="col-12 col-sm-6">
                            <q-input v-model="form.profile.middle_name" label="Middle Name" dense outlined hide-bottom-space />
                        </div>

                        <div class="col-12 col-sm-6">
                            <q-input v-model="form.profile.last_name" label="Last Name" dense outlined
                                :rules="[val => !!val || 'Required']" hide-bottom-space />
                        </div>

                        <div class="col-12 col-sm-6">
                            <q-input v-model="form.profile.suffix" label="Suffix" dense outlined hide-bottom-space />
                        </div>

                        <div class="col-12 col-sm-6">
                            <q-toggle v-model="form.is_active" label="Active" />
                        </div>

                        <div class="col-12 col-sm-6">
                            <q-toggle v-model="form.is_superuser" label="Superuser" />
                        </div>

                        <div class="col-12">
                            <q-select v-model="form.units" v-model:input-value="unitSearch"
                                :options="filteredUnitOptions" option-value="id" option-label="name" emit-value
                                map-options multiple use-chips use-input input-debounce="300" @filter="filterUnits"
                                @update:model-value="onSelectUnit" :fill-input="false" label="Units" outlined dense />
                        </div>

                        <div class="col-12 col-sm-6">
                            <q-select v-model="form.primary_unit" :options="filteredUnits" option-value="id"
                                option-label="name" emit-value map-options label="Primary Unit" outlined dense />
                        </div>

                    </div>

                </q-form>
            </q-card-section>

            <q-separator />

            <q-card-actions  align="right">
                <q-btn flat label="Cancel" v-close-popup />
                <q-btn color="primary" :label="isEdit ? 'Update' : 'Create'" @click="handleSubmit" :loading="loading" />
            </q-card-actions>

        </q-card>
    </q-dialog>
</template>

<script setup>
import { ref, computed, onMounted, reactive, watch } from 'vue'
import { useCoreStore } from 'src/stores/core'

const coreStore = useCoreStore()

const props = defineProps({
    modelValue: Boolean,
    data: Object,
    loading: Boolean
})

const emit = defineEmits(['update:modelValue', 'submit'])

const model = computed({
    get: () => props.modelValue,
    set: val => emit('update:modelValue', val)
})

const isEdit = computed(() => !!props.data)

// Form State
const form = reactive({
    email: '',
    is_active: true,
    is_superuser: false,
    profile: {
        first_name: '',
        middle_name: '',
        last_name: '',
        suffix: ''
    },
    units: [],
    primary_unit: null
})

const filteredUnits = computed(() => {
    return coreStore.units.filter(u =>
        form.units.includes(u.id)
    )
})

// Filter units
const filteredUnitOptions = ref([])

const unitSearch = ref('')

function onSelectUnit() {
  unitSearch.value = ''
}

function filterUnits(val, update) {
    update(() => {
        const needle = val.toLowerCase()

        filteredUnitOptions.value = coreStore.units.filter(unit =>
            unit.name.toLowerCase().includes(needle) ||
            unit.short_code?.toLowerCase().includes(needle)
        )
    })
}

// Check if data prop changes
watch(
    () => props.data,
    (val) => {
        if (val) {
            form.email = val.email || ''
            form.is_active = val.is_active ?? false
            form.is_superuser = val.is_superuser ?? false

            form.profile.first_name = val.profile?.first_name || ''
            form.profile.middle_name = val.profile?.middle_name || ''
            form.profile.last_name = val.profile?.last_name || ''
            form.profile.suffix = val.profile?.suffix || ''

            const units = val.user_units || []

            form.units = units.map(u => u.unit)
            form.primary_unit = units.find(u => u.is_primary)?.unit || null
        } else {
            resetForm()
        }
    },
    { immediate: true }
)

watch(() => form.units, (newUnits) => {
    if (!newUnits.includes(form.primary_unit)) {
        form.primary_unit = null
    }
})

// Reset
function resetForm() {
    form.email = ''
    form.is_active = false
    form.is_superuser = false
    form.profile.first_name = ''
    form.profile.middle_name = ''
    form.profile.last_name = ''
    form.profile.suffix = ''
    form.units = []
    form.primary_unit = null
}

// Submit
function handleSubmit() {
    emit('submit', { ...form })
}

onMounted(() => {
    coreStore.fetchUnits()
    filteredUnitOptions.value = coreStore.units
})
</script>
