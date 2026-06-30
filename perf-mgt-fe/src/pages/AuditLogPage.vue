<template>
    <div class="q-pa-md">
        <PageComboHeader title="Audit Logs" :breadcrumbs="[
            { label: 'Home', to: '/admin/dashboard' },
            { label: 'Admin' },
            { label: 'Audit Logs' }
        ]" :show-filter="false" />
    </div>
</template>

<script setup>
import PageComboHeader from 'src/components/PageComboHeader.vue';


</script>
    