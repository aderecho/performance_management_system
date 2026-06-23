<template>
    <div class="row items-center justify-center ">
        <q-btn size="sm" flat round color="dark-grey" @click="$emit('view', row)">
            <Eye :size="18" :stroke-width="2" />
            <q-tooltip>View</q-tooltip>
        </q-btn>

        <q-btn size="sm" flat round color="secondary" @click="$emit('edit', row)">
            <SquarePen :size="18" :stroke-width="2" />
            <q-tooltip>Edit</q-tooltip>
        </q-btn>

        <q-btn size="sm" flat round color="negative" @click="$emit('delete', row)">
            <Trash2 :size="18" :stroke-width="2" />
            <q-tooltip>Delete</q-tooltip>
        </q-btn>


    </div>
</template>

<script setup>
import { Eye, SquarePen, Trash2 } from 'lucide-vue-next'

defineProps({
    row: {
        type: Object,
        required: true
    }
})

defineEmits(['view', 'edit', 'delete'])
</script>
