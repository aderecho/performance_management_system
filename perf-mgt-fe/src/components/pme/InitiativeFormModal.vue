<template>
  <q-dialog :model-value="modelValue" @update:model-value="close">
    <q-card class="pme-initiative-dialog rounded-lg shadow-8">
      <!-- HEADER -->
      <q-card-section class="pme-initiative-header row items-center no-wrap q-pa-md">
        <div class="pme-initiative-header-icon">
          <component :is="isEdit ? SquarePen : Ruler" :size="20" :stroke-width="2.2" />
        </div>
        <div class="min-w-0 q-ml-md col">
          <div class="text-h6 text-weight-bold leading-snug">
            {{ isEdit ? 'Edit Initiative' : 'Add Initiative' }}
          </div>
          <div class="text-caption text-blue-grey-6">
            {{
              isEdit
                ? 'Update the details of this initiative.'
                : 'Create a new initiative for a performance measure.'
            }}
          </div>
        </div>
        <q-btn flat round dense icon="close" color="grey-7" class="flex-none" @click="close(false)">
          <q-tooltip>Close</q-tooltip>
        </q-btn>
      </q-card-section>

      <q-separator />

      <q-form @submit.prevent="onSubmit">
        <q-card-section class="pme-initiative-body q-pa-md q-gutter-y-md">
          <!-- Indicator -->
          <div>
            <q-select
              v-model="item"
              :options="filteredItemOptions"
              label="Performance Measure"
              emit-value
              map-options
              dense
              options-dense
              outlined
              use-input
              input-debounce="200"
              clearable
              class="rounded-input"
              :disable="!isEdit && !itemOptions.length"
              popup-content-class="pme-initiative-item-menu"
              :error="!!itemError"
              :error-message="itemError"
              @filter="filterItems"
            >
              <template #no-option>
                <q-item>
                  <q-item-section class="text-grey-7">
                    No matching performance measures.
                  </q-item-section>
                </q-item>
              </template>
            </q-select>

            <div v-if="!isEdit && !itemOptions.length" class="text-caption text-negative q-mt-xs">
              No authorized performance measures available for your unit.
            </div>
          </div>

          <!-- Description -->
          <q-input
            v-model="description"
            label="Description"
            dense
            outlined
            class="rounded-input"
            :error="!!descriptionError"
            :error-message="descriptionError"
          />

          <div class="row q-col-gutter-md">
            <div class="col-12 col-sm-6">
              <q-input
                v-model.number="value"
                type="number"
                label="Accomplishment Value"
                dense
                outlined
                class="rounded-input"
                :error="!!valueError"
                :error-message="valueError"
              />
            </div>

            <div class="col-12 col-sm-6">
              <q-input
                v-model="target_date"
                label="Target Date"
                dense
                outlined
                class="rounded-input"
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
          <q-input
            v-model="remarks"
            type="textarea"
            label="Remarks"
            dense
            outlined
            autogrow
            class="rounded-input"
            :error="!!remarksError"
            :error-message="remarksError"
          />
        </q-card-section>

        <q-separator />

        <q-card-actions align="right" class="q-pa-md">
          <q-btn flat label="Cancel" color="grey-7" @click="close(false)" />
          <q-btn
            type="submit"
            unelevated
            label="Submit"
            color="primary"
            class="rounded-md q-px-lg"
            :disable="!canSubmit"
            :loading="isSubmitting || loading"
          />
        </q-card-actions>
      </q-form>
    </q-card>
  </q-dialog>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useForm, useField } from 'vee-validate'
import { toTypedSchema } from '@vee-validate/zod'
import { initiativeSchema } from 'src/validators/initiative.schema'
import { today } from 'src/helpers/date'
import { Ruler, SquarePen } from 'lucide-vue-next'

const emit = defineEmits(['update:modelValue', 'submitted'])

const props = defineProps({
  modelValue: Boolean,
  items: {
    type: Array,
    required: true,
  },
  initiative: {
    type: Object,
    default: null,
  },
  loading: {
    type: Boolean,
    default: false,
  },
})

// Validation
const { handleSubmit, resetForm, isSubmitting, setValues } = useForm({
  validationSchema: toTypedSchema(initiativeSchema),
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
  { immediate: true },
)

// Submit
const isEdit = computed(() => !!props.initiative)

const flattenItems = (items, result = []) => {
  for (const i of items) {
    if (i.target !== null) result.push(i)
    if (i.children?.length) flattenItems(i.children, result)
  }
  return result
}

const authorizedItemOptions = computed(() =>
  flattenItems(props.items)
    .filter((i) => i.can_submit_initiative)
    .map((i) => ({
      label: `${i.code} ${i.name}`,
      value: i.id,
    })),
)

const currentItemOption = computed(() => {
  if (!props.initiative?.item) {
    return null
  }

  return {
    label: props.initiative.item_name || 'Selected performance measure',
    value: props.initiative.item,
  }
})

const itemOptions = computed(() => {
  if (!isEdit.value) {
    return authorizedItemOptions.value
  }

  if (
    currentItemOption.value &&
    !authorizedItemOptions.value.some((option) => option.value === currentItemOption.value.value)
  ) {
    return [currentItemOption.value, ...authorizedItemOptions.value]
  }

  return authorizedItemOptions.value
})

//SEARCHABLE DROPDOWN
const filteredItemOptions = ref([])

watch(
  itemOptions,
  (options) => {
    filteredItemOptions.value = options
  },
  { immediate: true },
)

function filterItems(search, update) {
  update(() => {
    const needle = search.trim().toLowerCase()

    filteredItemOptions.value = needle
      ? itemOptions.value.filter((option) => option.label.toLowerCase().includes(needle))
      : itemOptions.value
  })
}

const canSubmit = computed(() => isEdit.value || itemOptions.value.length > 0)

const onSubmit = handleSubmit((values) => {
  emit('submitted', values)
})

const close = (val = false) => {
  emit('update:modelValue', val)
}
</script>
