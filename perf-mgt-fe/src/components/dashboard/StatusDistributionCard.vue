<template>
  <q-card flat bordered class="bg-white full-height rounded-borders" :style="cardStyle">
    <q-card-section class="row items-center q-col-gutter-lg q-pa-lg" :style="sectionStyle">
      <div class="col-12 col-sm-6 row justify-center">
        <div
          class="relative-position"
          :style="donutStyle"
        >
          <div class="absolute-center bg-white" :style="innerCircleStyle"></div>

          <div class="absolute-full column flex-center text-center" style="z-index: 1">
            <strong class="text-dark text-weight-bolder" style="font-size: 36px; line-height: 1">
              {{ total }}
            </strong>
            <span class="text-blue-grey-8 text-weight-bold q-mt-md">{{ centerLabel }}</span>
          </div>
        </div>
      </div>

      <div class="col-12 col-sm-6 column">
        <div
          v-for="item in normalizedItems"
          :key="item.key"
          class="row items-center justify-between no-wrap q-py-sm"
          style="gap: 14px; border-bottom: 1px dashed #d8dee8"
        >
          <div class="row items-center no-wrap q-gutter-sm">
            <span
              :style="{
                backgroundColor: item.color,
                width: '12px',
                height: '12px',
                border: '2px solid #e8edf5',
                borderRadius: '50%'
              }"
            ></span>
            <span class="text-body2 text-dark">{{ item.label }}</span>
          </div>

          <strong class="text-dark">{{ item.percent }}%</strong>
        </div>
      </div>
    </q-card-section>
  </q-card>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  total: { type: Number, default: 0 },
  items: { type: Array, default: () => [] },
  width: { type: String, default: '100%' },
  height: { type: String, default: '100%' },
  minHeight: { type: String, default: '292px' },
  donutSize: { type: String, default: '232px' },
  innerCircleSize: { type: String, default: '66%' },
  centerLabel: { type: String, default: 'Measures' }
})

const cardStyle = computed(() => ({
  width: props.width,
  height: props.height
}))

const sectionStyle = computed(() => ({
  minHeight: props.minHeight
}))

const normalizedItems = computed(() => {
  return props.items.map(item => {
    const value = Number(item.value || 0)
    const percent = item.percent !== undefined
      ? Number(item.percent || 0)
      : props.total
        ? Math.round((value / props.total) * 100)
        : 0

    return {
      ...item,
      percent: Math.max(0, Math.min(percent, 100))
    }
  })
})

const innerCircleStyle = computed(() => ({
  width: props.innerCircleSize,
  height: props.innerCircleSize,
  borderRadius: '50%'
}))

const donutStyle = computed(() => {
  const baseStyle = {
    width: `min(${props.donutSize}, 100%)`,
    aspectRatio: '1',
    borderRadius: '50%'
  }

  if (!props.total) {
    return {
      ...baseStyle,
      background: '#e5e7eb'
    }
  }

  let current = 0
  const segments = normalizedItems.value.map(item => {
    const start = current
    const end = current + item.percent
    current = end
    return `${item.color} ${start}% ${end}%`
  })

  if (current < 100) {
    segments.push(`#e5e7eb ${current}% 100%`)
  }

  return {
    ...baseStyle,
    background: `conic-gradient(${segments.join(', ')})`
  }
})
</script>
