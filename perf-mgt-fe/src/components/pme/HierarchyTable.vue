<style>
.hierarchy-table table {
  table-layout: fixed;
  width: 100%;
}
.hierarchy-table th:first-child,
.hierarchy-table td:first-child {
  width: 40%;
}
.hierarchy-table td {
  white-space: normal !important;
  word-break: break-word !important;
  overflow-wrap: anywhere !important;
}
</style>
<template>
  <q-markup-table class="hierarchy-table" v-if="items && items.length">
    <thead>
      <tr id="header">
        <th class="text-center text-weight-bold" >Performance Measure</th>
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
