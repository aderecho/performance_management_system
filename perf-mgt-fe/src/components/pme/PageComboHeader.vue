<template>
  <div class="q-mb-lg">
    <div class="flex items-center justify-between q-mb-xs">
      <div >
        <div class="text-h5 text-weight-bold">
          <slot name="title">
            {{ title }}
          </slot>
        </div>
        <q-breadcrumbs class="text-grey-7 q-mt-xs">
          <q-breadcrumbs-el v-for="(bc, index) in breadcrumbs" :key="index" :to="bc.to">
            <slot :name="`breadcrumb-${index}`" :breadcrumb="bc">
              {{ bc.label }}
            </slot>
          </q-breadcrumbs-el>
        </q-breadcrumbs>
      </div>

      <!-- BUTTONS -->
      <div class="flex items-center">
        <q-btn class="q-mr-sm" icon="add" :label=" $q.screen.lt.sm ? '' : 'Add New Initiative'" color="primary" @click="pmeStore.onAddInitiative" />
        <PageFilter @apply="forwardFilter" />
      </div>
    </div>

    <q-separator spaced />
  </div>
</template>

<script setup>
import PageFilter from 'src/components/pme/PageFilter.vue';
import { usePmeStore } from 'src/stores/pme';

const pmeStore = usePmeStore();

const emit = defineEmits(['apply'])

// Forward filter to parent (PME)
function forwardFilter(filters) {
  emit('apply', filters)
}

defineProps({
  title: {
    type: String,
    required: true
  },
  breadcrumbs: {
    type: Array,
    default: () => []
  },
  buttons: {
    type: Array,
    default: () => []
  }
})
</script>

<style scoped>
h1 {
  font-weight: 600;
}
</style>

<!-- 
USAGE

Template
<PageComboHeader
    title="Strategic Plan"
    :breadcrumbs="[
    { label: 'Home', to: '/' },
    { label: 'Planning', to: '/planning' },
    { label: 'Strategic Plan' }
    ]"
    :buttons="[
    { icon: 'add', label: 'New Initiative', color: 'primary', onClick: addInitiative },
    { icon: 'filter_alt', color: 'secondary', onClick: openFilter }
    ]"
/>
-->