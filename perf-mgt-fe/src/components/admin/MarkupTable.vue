<template>
  <q-table
    flat
    bordered
    :title="title"
    :rows="props.rows"
    :columns="props.columns"
    :row-key="props.rowKey"
    :filter="showSearch ? search : undefined"
  >
    <!-- SEARCH -->
    <template v-if="showSearch" v-slot:top-right>
      <q-input borderless dense debounce="300" v-model="search" placeholder="Search">
        <template v-slot:append>
          <q-icon name="search" />
        </template>
      </q-input>
    </template>

    <template v-slot:body-cell-is_active="props">
      <q-td :props="props">
        <q-chip :color="props.row.is_active ? 'positive' : 'negative'" text-color="white" dense size="sm" outline>
          {{ props.row.is_active ? 'Active' : 'Inactive' }}
        </q-chip>
      </q-td>
    </template>

    <template v-slot:body-cell-is_superuser="props">
      <q-td :props="props">
        <q-chip :color="props.row.is_superuser ? 'positive' : 'negative'" text-color="white" dense size="sm" outline>
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
  }
})

const emit = defineEmits(['view', 'edit', 'delete'])
const slots = useSlots()
const search = ref('')

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
