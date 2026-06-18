<template>
  <q-dialog :model-value="modelValue" @update:model-value="close">
    <q-card class="pme-accomplishment-dialog rounded-lg shadow-8">
      <q-form @submit.prevent="onSubmit">
        <q-card-section class="pme-accomplishment-body q-pa-md">
          <div class="pme-accomplishment-panel bg-white rounded-lg q-pa-md">
            <div class="pme-accomplishment-eyebrow text-blue-grey-6 text-weight-bold text-uppercase">
              Selected Initiative
            </div>
            <div class="pme-break-anywhere text-base text-weight-bold leading-snug q-mt-xs">
              {{ initiativeTitle }}
            </div>

            <div class="pme-accomplishment-meta-grid q-mt-md">
              <div class="bg-grey-1 rounded-lg q-pa-sm min-w-0">
                <div class="pme-accomplishment-eyebrow text-blue-grey-6 text-weight-bold text-uppercase">
                  Unit
                </div>
                <div class="pme-break-anywhere pme-accomplishment-meta-value text-weight-bold q-mt-xs">
                  {{ unitLabel }}
                </div>
              </div>
              <div class="bg-grey-1 rounded-lg q-pa-sm min-w-0">
                <div class="pme-accomplishment-eyebrow text-blue-grey-6 text-weight-bold text-uppercase">
                  Target Date
                </div>
                <div class="pme-break-anywhere pme-accomplishment-meta-value text-weight-bold q-mt-xs">
                  {{ targetDateLabel }}
                </div>
              </div>
              <div class="bg-grey-1 rounded-lg q-pa-sm min-w-0">
                <div class="pme-accomplishment-eyebrow text-blue-grey-6 text-weight-bold text-uppercase">
                  Actual Value
                </div>
                <div class="pme-break-anywhere pme-accomplishment-meta-value text-weight-bold q-mt-xs">
                  {{ valueLabel }}
                </div>
              </div>
            </div>
          </div>

          <div class="pme-accomplishment-panel bg-white rounded-lg q-pa-md">
            <div class="row items-center justify-between q-mb-sm">
              <div class="row items-center gap-2 text-weight-bold">
                <CalendarRange :size="18" :stroke-width="2.2" />
                <span>Reporting Period</span>
              </div>
              <q-badge color="primary" outline>Required</q-badge>
            </div>

            <q-select v-model="reporting_period" :options="reportingPeriodOptions"
              label="Choose the period where this was completed" option-value="id" option-label="label" emit-value
              map-options dense outlined class="rounded-input" popup-content-class="accomplishment-period-menu"
              :error="!!reportingPeriodError" :error-message="reportingPeriodError">
              <template #option="scope">
                <q-item v-bind="scope.itemProps">
                  <q-item-section avatar>
                    <div class="pme-accomplishment-period-dot">
                      <CalendarRange :size="15" :stroke-width="2.2" />
                    </div>
                  </q-item-section>
                  <q-item-section>
                    <q-item-label class="text-weight-medium">{{ scope.opt.label }}</q-item-label>
                  </q-item-section>
                </q-item>
              </template>

              <template #no-option>
                <q-item>
                  <q-item-section class="text-grey-7">
                    No reporting periods are available for this document.
                  </q-item-section>
                </q-item>
              </template>
            </q-select>
          </div>

          <div class="pme-accomplishment-panel pme-accomplishment-evidence-panel bg-white rounded-lg q-pa-md"
            :class="{ 'pme-accomplishment-evidence-panel--ready': hasEvidence }">
            <div class="row items-center justify-between q-mb-sm">
              <div class="row items-center gap-2 text-weight-bold">
                <Paperclip :size="18" :stroke-width="2.2" />
                <span>Evidence</span>
              </div>
              <q-badge color="secondary" outline>Optional</q-badge>
            </div>

            <div
              class="pme-evidence-dropzone relative-position rounded-lg column items-center justify-center q-py-md gap-1 cursor-pointer"
              :class="{ 'pme-evidence-dropzone--ready': hasEvidence }" @click="fileRef?.pickFiles()">
              <Upload class="text-primary" :size="24" :stroke-width="2" />
              <div class="text-weight-medium text-sm pme-break-anywhere text-center q-mt-xs">{{ selectedFileName }}
              </div>
              <div class="text-caption text-grey-6">{{ selectedFileMeta }}</div>
              <q-btn v-if="hasEvidence" flat round dense icon="close" size="xs"
                class="absolute-top-right q-ma-xs text-grey-6" @click.stop="file_path = null" />
            </div>
            <q-file ref="fileRef" v-model="file_path" class="hidden" :accept="acceptedFileTypes" />
          </div>
        </q-card-section>

        <q-card-actions class="pme-accomplishment-actions row items-center justify-end q-pa-md">
          <div class="row gap-2 flex-none">
            <q-btn flat label="Cancel" color="grey-7" @click="close(false)" />
            <q-btn type="submit" unelevated label="Mark Accomplished" class="rounded-md q-px-lg" color="primary"
              :loading="isSubmitting" />
          </div>
        </q-card-actions>
      </q-form>
    </q-card>
  </q-dialog>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useForm, useField } from 'vee-validate'
import { CalendarRange, Upload, Paperclip } from 'lucide-vue-next'

const props = defineProps({
  modelValue: Boolean,
  initiative: {
    type: Object,
    default: null,
  },
  reportingPeriods: {
    type: Array,
    default: () => [],
  },
})

const emit = defineEmits(['update:modelValue', 'submitted'])

const fileRef = ref(null)

const acceptedFileTypes = '.pdf,.doc,.docx,.xls,.xlsx,image/*'

const reportingPeriodOptions = computed(() => props.reportingPeriods)

const { handleSubmit, isSubmitting, resetForm } = useForm({
  initialValues: {
    reporting_period: null,
    file_path: null,
  },
})

const { value: reporting_period, errorMessage: reportingPeriodError } = useField(
  'reporting_period',
  (value) => (value ? true : 'Select a reporting period.'),
)
const { value: file_path } = useField('file_path')

const initiativeTitle = computed(() => props.initiative?.description || 'Selected initiative')
const unitLabel = computed(() => {
  const unit = props.initiative?.unit

  return unit?.short_code || unit?.name || '---'
})
const targetDateLabel = computed(() => props.initiative?.target_date || '---')
const valueLabel = computed(() => props.initiative?.value ?? '---')
const hasEvidence = computed(() => !!file_path.value)
const selectedFileName = computed(() => file_path.value?.name || 'Evidence file selected')
const selectedFileMeta = computed(() => {
  const file = file_path.value
  if (!file?.size) return 'Upload File'

  return `${(file.size / 1024 / 1024).toFixed(2)} MB`
})

const onSubmit = handleSubmit(async (values) => {
  emit('submitted', {
    reporting_period: values.reporting_period,
    file_path: values.file_path || null,
  })
})

watch(
  () => props.modelValue,
  (open) => {
    if (open) resetForm()
  },
)

const close = (val = false) => {
  emit('update:modelValue', val)
}
</script>
