<template>
  <q-card class="full-width">
    <q-card-section>

      <!-- HEADER -->
      <div class="row items-center justify-between q-mb-sm">
        <div class="text-caption text-grey-7">
          {{ title }}
        </div>

        <div
          :class="[
            'q-pa-xs rounded-borders',
            iconBgClass,
            iconTextClass
          ]"
        >
          <q-icon :name="icon" size="24px" />
        </div>
      </div>

      <div class="text-h5 text-weight-bold">
        {{ value }}
      </div>

      <div
        v-if="trend"
        :class="['text-caption', trendColorClass]"
      >
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
    default: 'secondary'
  },
  iconBg: {
    type: String,
    default: 'primary'
  }
})

const trendColorClass = `text-${props.trendColor}`
const iconBgClass = `bg-${props.iconBg}`
const iconTextClass = 'text-white'
</script>