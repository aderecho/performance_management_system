<template>
  <q-markup-table flat bordered class="hierarchy-table rounded-3xl" v-if="items && items.length">
    <thead>
      <tr id="header">
        <th class="text-left text-weight-bold" >Performance Measure</th>
        <th>Target</th>
        <th>Accomplishment</th>
        <th>Percentage</th>
      </tr>
    </thead>

    <tbody>
      <HierarchyRow
        v-for="item in items"
        :key="item.id"
        :item="item"
        :level="0"
        :document-id="documentId"
        :document="document"
        @open-initiatives="$emit('open-initiatives', $event)"
      />
    </tbody>
  </q-markup-table>
</template>

<script setup>
import HierarchyRow from './HierarchyRow.vue'

defineProps({
  items: {
    type: Array,
    required: true
  },
  documentId: {
    type: String,
    required: true
  },
  document: {
    type: Object,
    required: true
  }
})

defineEmits(['open-initiatives'])
</script>
