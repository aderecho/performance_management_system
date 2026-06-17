<style>
.wrap-cell {
  white-space: normal;
  word-break: break-word;
  overflow-wrap: anywhere;
}
</style>
<template>
  <tr
    :class="[{ 'cursor-pointer': item.target }, 'hover:bg-grey-2']"
    @click="handleClick"
  >
    <td class="wrap-cell">
      <span>{{ item.code }} {{ item.name }}</span>
    </td>

    <template v-if="item.target">
      <td class="text-center">
        <span v-if="item.target">
          {{ item.target }}
          <span v-if="item.unit_of_measure">
            {{ item.unit_of_measure.short_code }}
          </span>
        </span>
      </td>
      <td class="text-center">{{ item.total_accomplishment }}</td>
      <td class="text-center">
          <q-chip v-if="item.percent_achieved>=100" outline color="green" :label="item.percent_achieved" />
          <q-chip v-if="item.percent_achieved<100" outline color="red" :label="item.percent_achieved" />
      </td>
    </template>
    <template v-else>
      <td class="text-center" colspan="3"></td>
    </template>
  </tr>

  <template v-if="item.children && item.children.length">
    <HierarchyRow
      v-for="child in item.children"
      :key="child.id"
      :item="child"
      :level="level + 1"
      :document-id="documentId"
      :document="document"
      @open-initiatives="$emit('open-initiatives', $event)"
    />
  </template>
</template>

<script setup>
const props = defineProps({
  item: { type: Object, required: true },
  level: { type: Number, default: 0 },
  documentId: { type: String, required: true },
  document: { type: Object, required: true }
})

const emit = defineEmits(['open-initiatives'])

const handleClick = () => {
  if (props.item.target) {
    emit('open-initiatives', props.item);
  }
}
</script>
