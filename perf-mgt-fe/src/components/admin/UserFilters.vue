<template>
  <div class="row items-center gap-2 admin-user-filters">
    <q-select
      v-model="local.primary_unit"
      class="rounded-2xl admin-user-filter admin-user-filter--unit"
      :options="unitOptions"
      option-label="label"
      option-value="value"
      emit-value
      map-options
      outlined
      dense
      clearable
      label="Primary Unit"
      :loading="coreStore.loading.units"
      @update:model-value="emitChange"
    />

    <q-select
      v-model="local.is_active"
      class="rounded-2xl admin-user-filter"
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

    <q-select
      v-model="local.is_superuser"
      class="rounded-2xl admin-user-filter"
      :options="superUserOptions"
      option-label="label"
      option-value="value"
      emit-value
      map-options
      outlined
      dense
      clearable
      label="Super User"
      @update:model-value="emitChange"
    />
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, watch } from 'vue'
import { useCoreStore } from 'src/stores/core'

const props = defineProps({
  modelValue: { type: Object, default: () => ({}) },
})

const emit = defineEmits(['update:modelValue', 'change'])
const coreStore = useCoreStore()

const local = reactive({
  primary_unit: null,
  is_active: null,
  is_superuser: null,
})

const unitOptions = computed(() =>
  coreStore.units.map((unit) => ({
    label: unit.short_code ? `${unit.short_code} - ${unit.name}` : unit.name,
    value: unit.id,
  })),
)

const statusOptions = [
  { label: 'Active', value: 'true' },
  { label: 'Inactive', value: 'false' },
]

const superUserOptions = [
  { label: 'Yes', value: 'true' },
  { label: 'No', value: 'false' },
]

watch(
  () => props.modelValue,
  (value) => {
    local.primary_unit = value?.primary_unit || null
    local.is_active = value?.is_active || null
    local.is_superuser = value?.is_superuser || null
  },
  { immediate: true, deep: true },
)

function emitChange() {
  const filters = {
    primary_unit: local.primary_unit || null,
    is_active: local.is_active || null,
    is_superuser: local.is_superuser || null,
  }

  emit('update:modelValue', filters)
  emit('change', filters)
}

onMounted(async () => {
  if (coreStore.units.length) return

  try {
    await coreStore.fetchUnits()
  } catch {
    // The parent page handles user-facing loading errors.
  }
})
</script>

