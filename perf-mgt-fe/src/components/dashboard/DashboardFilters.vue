<template>
    <div class="row q-col-gutter-sm q-mb-md">
        <div v-if="showSearch" class="col-12 col-md">
            <q-input
                v-model="local.search"
                class="rounded-2xl"
                outlined
                dense
                clearable
                debounce="350"
                :placeholder="searchPlaceholder"
                @update:model-value="emitChange"
            >
                <template #prepend>
                    <q-icon name="search" />
                </template>
            </q-input>
        </div>

        <div
            v-for="filter in selectFilters"
            :key="filter.name"
            :class="filter.colClass || 'col-12 col-md-2'"
        >
            <q-select
                v-model="local[filter.name]"
                class="rounded-2xl"
                :options="filter.options"
                :option-label="filter.optionLabel || 'label'"
                :option-value="filter.optionValue || 'value'"
                :emit-value="filter.emitValue ?? true"
                :map-options="filter.mapOptions ?? true"
                outlined
                dense
                :clearable="filter.clearable ?? true"
                :label="filter.label"
                @update:model-value="emitChange"
            />
        </div>
    </div>
</template>

<script setup>
import { computed, reactive, watch } from 'vue'

const props = defineProps({
    modelValue: { type: Object, default: () => ({}) },
    searchPlaceholder: {
        type: String,
        default: 'Search objective or performance measure...',
    },
    showSearch: {
        type: Boolean,
        default: true,
    },
    selectFilters: { type: Array, default: () => [] },
})

const emit = defineEmits(['update:modelValue', 'change'])

const local = reactive({
    search: '',
})

const filterNames = computed(() => [
    ...(props.showSearch ? ['search'] : []),
    ...props.selectFilters.map((filter) => filter.name),
])

watch(
    [() => props.modelValue, filterNames],
    ([value, names]) => {
        names.forEach((name) => {
            local[name] = name === 'search'
                ? value?.[name] || ''
                : value?.[name] || null
        })

        Object.keys(local).forEach((name) => {
            if (!names.includes(name)) {
                delete local[name]
            }
        })
    },
    { immediate: true, deep: true }
)

function emitChange() {
    const filters = filterNames.value.reduce((payload, name) => {
        payload[name] = local[name] || null
        return payload
    }, {})

    emit('update:modelValue', filters)
    emit('change', filters)
}
</script>
