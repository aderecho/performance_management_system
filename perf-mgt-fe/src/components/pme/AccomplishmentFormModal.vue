<template>
  <q-dialog :model-value="modelValue" @update:model-value="close">
    <q-card class="q-pa-sm" style="width: 500px; max-width: 90vw">

      <q-card-section class="text-h6">
        Mark as Accomplished
      </q-card-section>

      <q-form @submit.prevent="onSubmit">
        <q-card-section class="q-gutter-xs">

          <q-select
            v-model="reporting_period"
            :options="reportingPeriodOptions"
            label="Reporting Period"
            emit-value
            map-options
            dense
            outlined
            :error="!!reportingPeriodError"
            :error-message="reportingPeriodError"
          />

        </q-card-section>

        <q-card-actions align="right" class="q-pr-md">
          <q-btn flat label="Cancel" color="grey" @click="close(false)" />
          <q-btn type="submit" label="Submit" color="primary" />
        </q-card-actions>
      </q-form>

    </q-card>
  </q-dialog>
</template>

<script setup>
import { useForm, useField } from 'vee-validate'
import { api } from 'boot/axios'

const props = defineProps({
  modelValue: Boolean,
  initiative: {
    type: Object,
    default: null
  },
  reportingPeriods: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:modelValue', 'submitted'])

const reportingPeriodOptions = props.reportingPeriods

const { handleSubmit } = useForm()
const { value: reporting_period, errorMessage: reportingPeriodError } =
  useField('reporting_period')

const onSubmit = handleSubmit(async (values) => {
  await api.post(`/pme/initiatives/${props.initiative.id}/accomplishments/`, {
    reporting_period: values.reporting_period.id
  })

  emit('submitted')
  close(false)
})

const close = (val = false) => {
  emit('update:modelValue', val)
}
</script>