<template>
  <q-dialog v-model="localModel">
    <q-card class="dialog-sm q-pa-md rounded-full">
      <q-card-section class="row items-center">
        <TriangleAlert :class="`text-${confirmColor} q-mr-sm`" />
        <div class="text-h6">{{ title }}</div>
      </q-card-section>

      <q-card-section>
        <slot> Are you sure you want to delete this item? </slot>
      </q-card-section>

      <q-card-actions align="right">
        <q-btn flat label="Cancel" color="grey-7" @click="cancel" />
        <q-btn unelevated :label="confirmLabel" :color="confirmColor" :loading="loading" @click="confirm" />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup>
import { computed } from 'vue'
import { TriangleAlert } from 'lucide-vue-next'

const props = defineProps({
  modelValue: Boolean,
  loading: { type: Boolean, default: false },
  title: { type: String, default: 'Confirm Deletion' },
  confirmLabel: { type: String, default: 'Delete' },
  confirmColor: { type: String, default: 'negative' },
})

const emit = defineEmits(['update:modelValue', 'confirmDelete'])

const localModel = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
})

const cancel = () => {
  emit('update:modelValue', false)
}

const confirm = () => {
  emit('confirmDelete')
}
</script> 
