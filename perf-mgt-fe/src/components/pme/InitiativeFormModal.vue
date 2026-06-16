<template>
  <q-dialog :model-value="modelValue" @update:model-value="close">
    <q-card class="q-pa-sm" style="width: 500px; max-width: 90vw">

      <q-card-section class="text-h6">
        {{ isEdit ? 'Edit Initiative' : 'Add Initiative' }}
      </q-card-section>

      <q-form @submit.prevent="onSubmit">
        <q-card-section class="q-gutter-xs">

          <!-- Indicator -->
          <q-select v-model="item" :options="itemOptions" label="Performance Measure" emit-value map-options dense outlined
            :error="!!itemError" :error-message="itemError" />

          <!-- Description -->
          <q-input v-model="description" label="Description" dense outlined :error="!!descriptionError"
            :error-message="descriptionError" />

          <div class="row">
  <div class="col-6 q-pr-sm">
    <q-input
      v-model.number="value"
      type="number"
      label="Accomplishment Value"
      dense
      outlined
      :error="!!valueError"
      :error-message="valueError"
    />
  </div>

  <div class="col-6">
    <q-input
      v-model="target_date"
      label="Target Date"
      dense
      outlined
      :error="!!targetDateError"
      :error-message="targetDateError"
    >
      <template #append>
        <q-icon name="event" class="cursor-pointer">
          <q-popup-proxy cover transition-show="scale" transition-hide="scale">
            <q-date v-model="target_date" mask="YYYY-MM-DD" />
          </q-popup-proxy>
        </q-icon>
      </template>
    </q-input>
  </div>
</div>

          <!-- Remarks -->
          <q-input v-model="remarks" type="textarea" label="Remarks" dense outlined :error="!!remarksError"
            :error-message="remarksError" class="q-pb-none" />

        </q-card-section>

        <q-card-actions align="right" class="q-pr-md">
          <q-btn label="Cancel" outline color="grey" @click="close(false)" />
          <q-btn type="submit" label="Submit" color="primary" :loading="isSubmitting" />
        </q-card-actions>
      </q-form>

    </q-card>
  </q-dialog>
</template>

<script setup>
import { computed, watch } from 'vue'
import { useForm, useField } from 'vee-validate'
import { toFormValidator } from '@vee-validate/zod'
import { initiativeSchema } from 'src/validators/initiative.schema'
import { usePmeStore } from 'src/stores/pme'
import { today } from 'src/helpers/date'

const emit = defineEmits(['update:modelValue', 'submitted'])

const props = defineProps({
  modelValue: Boolean,
  items: {
    type: Array,
    required: true,
  },
  initiative: {
    type: Object,
    default: null
  }
})

const pmeStore = usePmeStore()

// Validation
const { handleSubmit, resetForm, isSubmitting, setValues } = useForm({
  validationSchema: toFormValidator(initiativeSchema),
  initialValues: {
    item: null,
    description: '',
    value: null,
    target_date: today(),
    remarks: '',
  },
})

const { value: item, errorMessage: itemError } = useField('item')
const { value: description, errorMessage: descriptionError } = useField('description')
const { value: value, errorMessage: valueError } = useField('value')
const { value: target_date, errorMessage: targetDateError } = useField('target_date')
const { value: remarks, errorMessage: remarksError } = useField('remarks')

watch(
  [() => props.modelValue, () => props.initiative],
  ([open, initiative]) => {
    if (!open) return

    if (initiative) {
      setValues({
        item: initiative.item,
        description: initiative.description,
        value: parseFloat(initiative.value),
        target_date: initiative.target_date,
        remarks: initiative.remarks ?? '',
      })
    } else {
      resetForm()
    }
  },
  { immediate: true }
)

const flattenItems = (items, result = []) => {
  for (const i of items) {
    if (i.target !== null) result.push(i)
    if (i.children?.length) flattenItems(i.children, result)
  }
  return result
}

const itemOptions = computed(() =>
  flattenItems(props.items).map(i => ({
    label: `${i.code} ${i.name}`,
    value: i.id,
  }))
)

// Submit
const isEdit = computed(() => !!props.initiative)

const onSubmit = handleSubmit(async (values) => {
  if (isEdit.value) {
    await pmeStore.updateInitiative(props.initiative.id, values)

    pmeStore.fetchInitiatives(pmeStore.selectedIndicator.id) // Should be indicator_id
  } else {
    await pmeStore.createSubmission(values)
  }

  emit('submitted')
  close(false)
})

const close = (val = false) => {
  emit('update:modelValue', val)
}
</script>
