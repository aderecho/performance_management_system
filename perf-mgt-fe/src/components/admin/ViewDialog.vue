<template>
  <q-dialog v-model="model">
    <q-card class="dialog-view">
      <q-card-section class="row items-center justify-between">
        <div class="text-h6">{{ title }}</div>
        <q-btn icon="close" flat round dense v-close-popup />
      </q-card-section>

      <q-separator />

      <q-card-section>
        <q-card-section>
          <div v-if="loading" class="text-center q-pa-md">
            <q-spinner />
          </div>

          <!-- GRID -->
          <div v-else class="row q-col-gutter-md">
            <div v-for="field in fields" :key="field.key" class="col-12 col-sm-6">
              <div class="q-pa-sm bordered rounded-borders bg-grey-1">
                <!-- LABEL -->
                <div class="text-caption text-grey-7">
                  {{ field.label }}
                </div>

                <!-- VALUE -->
                <div class="text-body1 text-weight-medium">
                  <!-- BADGE -->
                  <q-chip
                    v-if="field.type === 'badge'"
                    :color="getBadgeConfig(field, data).color"
                    text-color="white"
                    dense
                    size="md"
                    class="q-px-md q-py-sm"
                  >
                    {{ getBadgeConfig(field, data).label }}
                  </q-chip>

                  <!-- DEFAULT -->
                  <span v-else>
                    {{ formatFieldValue(field, resolveFieldValue(data, field.key), data) }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </q-card-section>
      </q-card-section>
    </q-card>
  </q-dialog>
</template>

<script setup>
import { computed } from 'vue'
import { resolveFieldValue, formatFieldValue, getBadgeConfig } from 'src/helpers/fieldFormatter'

const props = defineProps({
  modelValue: Boolean,
  title: String,
  data: Object,
  fields: {
    type: Array,
    default: () => [],
  },
  loading: Boolean,
})

const emit = defineEmits(['update:modelValue'])

const model = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
})
</script>
