<template>
  <component
    :is="containerComponent"
    v-bind="containerAttrs"
    :class="containerClasses"
    :style="cardVars"
  >
    <component
      :is="sectionComponent"
      :class="sectionClasses"
      :style="sectionVars"
    >
      <div :class="donutColumnClasses">
        <div class="relative-position status-distribution-donut" :style="donutVars">
          <div
            class="absolute-center bg-white status-distribution-inner-circle"
            :style="innerCircleVars"
          ></div>

          <div class="absolute-full column flex-center text-center z-1">
            <strong :class="centerValueClass">
              {{ displayCenterValue }}{{ centerSuffix }}
            </strong>
            <span :class="centerLabelClass">{{ centerLabel }}</span>
          </div>
        </div>
      </div>

      <div v-if="showLegend" class="col-12 col-sm-6 column">
        <div
          v-for="item in normalizedItems"
          :key="item.key"
          class="row items-center justify-between no-wrap q-py-sm gap-14 border-b border-dashed border-blue-grey-200"
        >
          <div class="row items-center no-wrap q-gutter-sm">
            <span class="status-distribution-dot" :style="statusDotVars(item.color)"></span>
            <span class="text-body2 text-dark">{{ item.label }}</span>
          </div>

          <strong class="text-dark">{{ item.percent }}%</strong>
        </div>
      </div>
    </component>
  </component>
</template>

<script setup>
import { computed } from 'vue'
import { QCard, QCardSection } from 'quasar'

const props = defineProps({
  total: { type: Number, default: 0 },
  items: { type: Array, default: () => [] },
  variant: { type: String, default: 'card' },
  showLegend: { type: Boolean, default: true },
  width: { type: String, default: '100%' },
  height: { type: String, default: '100%' },
  minHeight: { type: String, default: '292px' },
  donutSize: { type: String, default: '232px' },
  innerCircleSize: { type: String, default: '66%' },
  centerValue: { type: [Number, String], default: null },
  centerLabel: { type: String, default: 'Measures' },
  centerSuffix: { type: String, default: '' },
  centerValueClass: {
    type: String,
    default: 'text-dark text-weight-bolder text-4xl leading-none',
  },
  centerLabelClass: {
    type: String,
    default: 'text-blue-grey-8 text-weight-bold q-mt-md',
  },
})

const isInline = computed(() => props.variant === 'inline')

const containerComponent = computed(() => (isInline.value ? 'div' : QCard))

const containerAttrs = computed(() => (isInline.value ? {} : { flat: true, bordered: true }))

const containerClasses = computed(() => [
  'bg-white status-distribution-card',
  isInline.value ? 'status-distribution-card--inline' : 'full-height rounded-borders',
])

const sectionComponent = computed(() => (isInline.value ? 'div' : QCardSection))

const sectionClasses = computed(() => [
  'row items-center status-distribution-section',
  isInline.value ? 'q-pa-none' : 'q-col-gutter-lg q-pa-lg',
])

const donutColumnClasses = computed(() => [
  'row justify-center',
  props.showLegend ? 'col-12 col-sm-6' : 'col-12',
])

const cardVars = computed(() => ({
  '--status-distribution-width': props.width,
  '--status-distribution-height': props.height,
}))

const sectionVars = computed(() => ({
  '--status-distribution-min-height': props.minHeight,
}))

const normalizedItems = computed(() => {
  return props.items.map((item) => {
    const value = Number(item.value || 0)
    const percent =
      item.percent !== undefined
        ? Number(item.percent || 0)
        : props.total
          ? Math.round((value / props.total) * 100)
          : 0

    return {
      ...item,
      percent: Math.max(0, Math.min(percent, 100)),
    }
  })
})

const displayCenterValue = computed(() => props.centerValue ?? props.total)

const innerCircleVars = computed(() => ({
  '--status-distribution-inner-size': props.innerCircleSize,
}))

const donutVars = computed(() => {
  if (!props.total) {
    return {
      '--status-distribution-donut-size': props.donutSize,
      '--status-distribution-donut-background': '#e5e7eb',
    }
  }

  let current = 0
  const segments = normalizedItems.value.map((item) => {
    const start = current
    const end = current + item.percent
    current = end
    return `${item.color} ${start}% ${end}%`
  })

  if (current < 100) {
    segments.push(`#e5e7eb ${current}% 100%`)
  }

  return {
    '--status-distribution-donut-size': props.donutSize,
    '--status-distribution-donut-background': `conic-gradient(${segments.join(', ')})`,
  }
})

function statusDotVars(color) {
  return {
    '--status-distribution-dot-color': color,
  }
}
</script>
