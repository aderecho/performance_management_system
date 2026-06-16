<template>
  <div class="q-mb-lg">
    <!-- Title -->
    <div class="flex items-center justify-between q-mb-xs">
      <h1 class="text-h5 q-mb-none">{{ title }}</h1>
    </div>

    <!-- Breadcrumbs -->
    <q-breadcrumbs
      class="text-grey-7"
      active-color="primary"
      separator=">"
    >
      <q-breadcrumbs-el
        v-for="(crumb, index) in breadcrumbs"
        :key="index"
        :label="crumb.label || crumb"
        :icon="crumb.icon"
        :to="crumb.to"
        :disable="!crumb.to"
      />
    </q-breadcrumbs>

    <q-separator spaced />
  </div>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    required: true
  },
  breadcrumbs: {
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
<PageHeader title="User Management" :breadcrumbs="[
    { label: 'Home', to: '/' },
    { label: 'Strategic Plan' },
]" />

Script
import PageHeader from 'src/components/PageHeader.vue'
-->
