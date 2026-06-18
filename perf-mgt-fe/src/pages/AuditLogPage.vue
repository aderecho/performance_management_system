<template>
    <div class="q-pa-md">
        <PageComboHeader title="Audit Log" :breadcrumbs="[
            { label: 'Home', to: '/dashboard' },
            { label: 'Admin' },
            { label: 'Audit Log' }
        ]" :show-filter="false" />
    </div>
</template>

<script setup>
import PageComboHeader from 'src/components/PageComboHeader.vue';


</script>