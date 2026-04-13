<template>
  <q-dialog v-model="localModel">
    <q-card style="width: 400px; max-width: 90vw;">
      <q-card-section class="row items-center">
        <q-icon name="warning" color="negative" size="md" class="q-mr-sm" />
        <div class="text-h6">Confirm Revert</div>
      </q-card-section>

      <q-card-section>
        <slot>
          Are you sure you want to revert accomplishment?
        </slot>
      </q-card-section>

      <q-card-actions align="right">
        <q-btn flat label="Cancel" color="primary" @click="cancel" />
        <q-btn
          unelevated
          label="Revert"
          color="accent"
          :loading="loading"
          @click="confirm"
        />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: Boolean,
  loading: { type: Boolean, default: false },
})

const emit = defineEmits([
  'update:modelValue',
  'confirmRevert',
])

const localModel = computed({
  get: () => props.modelValue,
  set: val => emit('update:modelValue', val),
})

const cancel = () => {
  emit('update:modelValue', false)
}

const confirm = () => {
  emit('confirmRevert')
}
</script>