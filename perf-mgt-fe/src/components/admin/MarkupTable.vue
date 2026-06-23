<template>
  <q-table
    flat
    bordered
    :rows="props.rows"
    :columns="props.columns"
    :row-key="props.rowKey"
    :filter="showSearch ? search : undefined"
    v-model:pagination="pagination"
    :table-header-class="tableHeaderClass"
    class="rounded-3xl"
  >
    <template v-slot:top>
      <div class="row full-width items-center justify-between q-gutter-y-sm">
        <div class="col-12 col-sm">
          <div v-if="title" :class="[titleWeightClass, 'markup-table-title']" :style="titleVars">
            {{ title }}
          </div>
        </div>

        <div class="col-12 col-sm-auto">
          <div class="row items-center justify-end gap-2">
            <slot name="filters" />

            <q-input
              v-if="showSearch"
              v-model="search"
              class="rounded-2xl markup-table-search flex-none"
              :style="searchVars"
              outlined
              dense
              clearable
              debounce="300"
              :placeholder="searchPlaceholder"
            >
              <template v-slot:prepend>
                <q-icon name="search" />
              </template>
            </q-input>
          </div>
        </div>
      </div>
    </template>

    <template v-slot:body-cell-is_active="props">
      <q-td :props="props">
        <q-chip
          :color="props.row.is_active ? 'green-1' : 'red-1'"
          :text-color="props.row.is_active ? 'green-9' : 'red-9'"
          class="q-px-md text-weight-medium status-badge"
        >
          <span class="status-dot" :class="props.row.is_active ? 'bg-green-9' : 'bg-red-9'" />
          {{ props.row.is_active ? 'Active' : 'Inactive' }}
        </q-chip>
      </q-td>
    </template>

    <template v-slot:body-cell-is_superuser="props">
      <q-td :props="props">
        <q-chip
          :color="props.row.is_superuser ? 'green-1' : 'grey-3'"
          :text-color="props.row.is_superuser ? 'green-9' : 'red-8'"
          class="q-px-md text-weight-medium status-badge"
        >
          <span class="status-dot" :class="props.row.is_superuser ? 'bg-green-9' : 'bg-red-9'" />
          {{ props.row.is_superuser ? 'Yes' : 'No' }}
        </q-chip>
      </q-td>
    </template>

    <template v-slot:body-cell-actions="props">
      <q-td :props="props">
        <slot name="body-cell-actions" v-bind="props">
          <RowActions
            :row="props.row"
            @view="emit('view', $event)"
            @edit="emit('edit', $event)"
            @delete="emit('delete', $event)"
          />
        </slot>
      </q-td>
    </template>

    <template v-for="slotName in passthroughSlotNames" :key="slotName" #[slotName]="slotProps">
      <slot :name="slotName" v-bind="slotProps || {}" />
    </template>
  </q-table>
</template>

<script setup>
import { computed, ref, useSlots } from 'vue'
import RowActions from 'src/components/RowActions.vue'

const props = defineProps({
  title: String,
  rows: Array,
  columns: Array,
  rowKey: {
    type: String,
    default: 'id',
  },
  showSearch: {
    type: Boolean,
    default: true,
  },
  tableHeaderClass: {
    type: String,
    default: '',
  },
  titleFontSize: {
    type: String,
    default: '20px',
  },
  titleWeightClass: {
    type: String,
    default: 'text-weight-bold',
  },
  searchPlaceholder: {
    type: String,
    default: 'Search',
  },
  searchWidth: {
    type: String,
    default: '280px',
  },
})

const emit = defineEmits(['view', 'edit', 'delete'])
const slots = useSlots()
const search = ref('')
const pagination = ref({
  page: 1,
  rowsPerPage: 10,
})

const titleVars = computed(() => ({
  '--markup-table-title-font-size': props.titleFontSize,
}))

const searchVars = computed(() => ({
  '--markup-table-search-width': props.searchWidth,
}))

const reservedSlotNames = [
  'default',
  'top-right',
  'filters',
  'body-cell-is_active',
  'body-cell-is_superuser',
  'body-cell-actions',
]

const passthroughSlotNames = computed(() => {
  return Object.keys(slots).filter((slotName) => !reservedSlotNames.includes(slotName))
})

function resetPagination() {
  pagination.value = {
    ...pagination.value,
    page: 1,
  }
}

defineExpose({
  resetPagination,
})
</script>

<style scoped>

</style>
