<template>
  <q-dialog v-model="model">
    <q-card class="view-dialog" :style="{ width }">
      <!-- HEADER -->
      <slot name="header">
        <q-card-section class="view-dialog__header row items-center no-wrap q-gutter-sm">
          <div class="view-dialog__icon">
            <component :is="icon" :size="20" :stroke-width="2" />
          </div>
          <div class="col min-w-0">
            <div class="text-h6 leading-snug ellipsis">{{ title }}</div>
            <div v-if="subtitle" class="text-caption text-grey-7 ellipsis">{{ subtitle }}</div>
          </div>
          <q-btn icon="close" flat round dense aria-label="Close" v-close-popup />
        </q-card-section>
      </slot>

      <q-separator />

      <!-- BODY -->
      <q-card-section class="view-dialog__body">
        <div v-if="loading" class="column items-center q-py-lg text-grey-6">
          <q-spinner color="primary" size="28px" />
          <div class="text-caption q-mt-sm">Loading…</div>
        </div>

        <slot v-else />
      </q-card-section>

      <!-- OPTIONAL FOOTER -->
      <template v-if="$slots.actions">
        <q-separator />
        <q-card-actions align="right">
          <slot name="actions" />
        </q-card-actions>
      </template>
    </q-card>
  </q-dialog>
</template>

<script setup>
import { computed } from 'vue'
import { Eye } from 'lucide-vue-next'

const props = defineProps({
  modelValue: Boolean,
  title: {
    type: String,
    default: 'Details',
  },
  subtitle: {
    type: String,
    default: '',
  },
  // Any lucide-vue-next icon component (or other render component).
  icon: {
    type: [Object, Function],
    default: () => Eye,
  },
  loading: Boolean,
  width: {
    type: String,
    default: '560px',
  },
})

const emit = defineEmits(['update:modelValue'])

const model = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
})
</script>
