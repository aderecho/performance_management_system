<template>
  <q-table
    flat
    bordered
    :rows="props.rows"
    :columns="props.columns"
    :row-key="props.rowKey"
    :filter="showSearch ? search : undefined"
    :table-header-class="tableHeaderClass"
    style="border-radius: 16px;"
  >
    <template v-slot:top>
      <div class="row full-width items-center justify-between ">
        <div class="col-12 col-sm">
          <div v-if="title" :class="titleWeightClass" :style="titleStyle">
            {{ title }}
          </div>
        </div>

        <div v-if="showSearch" class="col-12 col-sm-auto">
          <q-input
            v-model="search"
            class="rounded-2xl"
            :style="searchStyle"
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
    </template>

    <template v-slot:body-cell-is_active="props">
      <q-td :props="props">
        <q-chip :color="props.row.is_active ? 'positive' : 'negative'" class="q-px-md q-py-sm" text-color="white" dense size="md" outline>
          {{ props.row.is_active ? 'Active' : 'Inactive' }}
        </q-chip>
      </q-td>
    </template>

    <template v-slot:body-cell-is_superuser="props">
      <q-td :props="props">
        <q-chip :color="props.row.is_superuser ? 'positive' : 'negative'" class="q-px-md" text-color="white" dense size="md" outline>
          {{ props.row.is_superuser ? 'Yes' : 'No' }}
        </q-chip>
      </q-td>
    </template>

    <template v-slot:body-cell-actions="props">
      <q-td :props="props">

        <RowActions :row="props.row" @view="emit('view', $event)" @edit="emit('edit', $event)" @delete="emit('delete', $event)" />

      </q-td>
    </template>

    <template
      v-for="slotName in passthroughSlotNames"
      :key="slotName"
      #[slotName]="slotProps"
    >
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
    default: 'id'
  },
  showSearch: {
    type: Boolean,
    default: true
  },
  tableHeaderClass: {
    type: String,
    default: ''
  },
  titleFontSize: {
    type: String,
    default: '20px'
  },
  titleWeightClass: {
    type: String,
    default: 'text-weight-bold'
  },
  searchPlaceholder: {
    type: String,
    default: 'Search'
  },
  searchWidth: {
    type: String,
    default: '280px'
  }
})

const emit = defineEmits(['view', 'edit', 'delete'])
const slots = useSlots()
const search = ref('')

const titleStyle = computed(() => ({
  fontSize: props.titleFontSize,
  lineHeight: 1.2
}))

const searchStyle = computed(() => ({
  width: props.searchWidth
}))

const reservedSlotNames = [
  'default',
  'top-right',
  'body-cell-is_active',
  'body-cell-is_superuser',
  'body-cell-actions'
]

const passthroughSlotNames = computed(() => {
  return Object.keys(slots).filter(slotName => !reservedSlotNames.includes(slotName))
})
</script>
