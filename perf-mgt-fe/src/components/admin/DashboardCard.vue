<template>
  <q-card flat bordered class="full-width shadow-8 rounded-3xl">
    <q-card-section>
      <!-- HEADER -->
      <div class="row items-center justify-between q-mb-sm">
        <div class="text-caption text-weight-bold text-black">
          {{ title }}
        </div>

        <div :class="['icon-soft', iconColorClass, iconBgClass]">
          <component :is="icon" :size="iconSize" :stroke-width="2" />
        </div>
      </div>

      <div class="text-h5 text-weight-bold">
        {{ value }}
      </div>

      <div v-if="trend" :class="['text-caption', trendColorClass]">
        {{ trend }}
      </div>
    </q-card-section>
  </q-card>
</template>

<script setup>
const props = defineProps({
  title: String,
  value: [String, Number],
  icon: String,
  trend: String,
  trendColor: {
    type: String,
    default: 'secondary',
  },
  iconColor: {
    type: String,
    default: 'primary',
  },
  iconSize: {
    type: Number,
    default: 24,
  },
  iconBgClass: {
    type: String,
    default: null,
  },
})

const trendColorClass = `text-${props.trendColor}`
const iconColorClass = `text-${props.iconColor}`
</script>
