<template>
    <div class="q-pa-md">
      <PageComboHeader title="Role Management" :breadcrumbs="[
            { label: 'Home', to: '/dashboard' },
            { label: 'Admin' },
            { label: 'Role Management' }
        ]" :show-filter="false"/>
    </div>
</template>

<script setup>
import PageComboHeader from 'src/components/PageComboHeader.vue'

</script>