<template>
  <div class="hierarchy-card rounded-3xl">
    <q-markup-table
      v-if="items && items.length"
      flat
      wrap-cells
      class="hierarchy-table"
    >
      <thead>
        <tr>
          <th class="text-left">Performance Measure</th>
          <th class="text-center">Target</th>
          <th class="text-center">Accomplishment</th>
          <th class="text-center">Achievement</th>
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

    <div v-else class="hierarchy-empty column flex-center text-center q-pa-xl">
      <ClipboardList :size="40" :stroke-width="1.5" class="text-grey-5 q-mb-sm" />
      <div class="text-subtitle1 text-grey-7">No performance measures</div>
      <div class="text-body2 text-grey-5">
        Items added to this document will appear here.
      </div>
    </div>
  </div>
</template>

<script setup>
import { ClipboardList } from 'lucide-vue-next'
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
