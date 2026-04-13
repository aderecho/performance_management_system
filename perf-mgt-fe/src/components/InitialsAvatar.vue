<template>
  <q-avatar
    :size="size"
    :color="color"
    text-color="white"
    class="flex items-center justify-center"
  >
    {{ displayInitials }}
  </q-avatar>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  firstName: {
    type: String,
    default: '',
  },
  lastName: {
    type: String,
    default: '',
  },
  size: {
    type: String,
    default: '32px',
  },
  color: {
    type: String,
    default: 'accent',
  },
  textColor: {
    type: String,
    default: 'white',
  },
})

const displayInitials = computed(() => {
  const first = props.firstName?.charAt(0) || ''
  const last = props.lastName?.charAt(0) || ''

  return (first + last).toUpperCase() || 'UP'
})
</script>