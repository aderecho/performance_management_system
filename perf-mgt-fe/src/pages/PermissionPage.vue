<template>
    <div class="q-pa-md">
      <PageComboHeader title="Permission Management" :breadcrumbs="[
            { label: 'Home', to: '/' },
            { label: 'Admin' },
            { label: 'Permission Management' }
        ]" :show-filter="false"/>
    </div>
</template>

<script setup>
import PageComboHeader from 'src/components/PageComboHeader.vue'

</script>