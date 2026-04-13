<template>
    <div class="row items-center justify-center q-gutter-xs">
        <q-btn size="sm" flat round icon="visibility" color="secondary" @click="$emit('view', row)">
            <q-tooltip>View</q-tooltip>
        </q-btn>

        <q-btn size="sm" flat round icon="edit" color="warning" @click="$emit('edit', row)">
            <q-tooltip>Edit</q-tooltip>
        </q-btn>

        <q-btn size="sm" flat round icon="delete" color="negative" @click="$emit('delete', row)">
            <q-tooltip>Delete</q-tooltip>
        </q-btn>


    </div>
</template>

<script setup>
defineProps({
    row: {
        type: Object,
        required: true
    }
})

defineEmits(['view', 'edit', 'delete'])
</script>