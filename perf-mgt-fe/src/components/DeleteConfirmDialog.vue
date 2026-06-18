<template>
  <q-dialog v-model="localModel">
    <q-card class="dialog-sm q-pa-md rounded-full">
      <q-card-section class="row items-center">
        <TriangleAlert class="text-negative q-mr-sm" />
        <div class="text-h6">Confirm Deletion</div>
      </q-card-section>

      <q-card-section>
        <slot> Are you sure you want to delete this item? </slot>
      </q-card-section>

      <q-card-actions align="right">
        <q-btn flat label="Cancel" color="grey-7" @click="cancel" />
        <q-btn unelevated label="Delete" color="negative" :loading="loading" @click="confirm" />
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
