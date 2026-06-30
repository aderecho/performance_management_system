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
  const total = Number(props.total || 0)
  const values = props.items.map((item) => Number(item.value || 0))
  const valueTotal = values.reduce((sum, value) => sum + value, 0)
  const isCompleteDistribution =
    total > 0 &&
    valueTotal === total &&
    props.items.every((item) => item.percent === undefined)

  if (isCompleteDistribution) {
    const percentages = roundedDistributionPercentages(values, total)

    return props.items.map((item, index) => ({
      ...item,
      percent: percentages[index],
    }))
  }

  return props.items.map((item, index) => {
    const percent =
      item.percent !== undefined
        ? Number(item.percent || 0)
        : total
          ? Math.round((values[index] / total) * 100)
          : 0

    return {
      ...item,
      percent: clampPercent(percent),
    }
  })
})

function roundedDistributionPercentages(values, total) {
  const parts = values.map((value, index) => {
    const exact = (value / total) * 100
    const floor = Math.floor(exact)

    return {
      index,
      value,
      floor,
      remainder: exact - floor,
    }
  })

  let remaining = 100 - parts.reduce((sum, part) => sum + part.floor, 0)
  const percentages = parts.map((part) => part.floor)

  parts
    .filter((part) => part.value > 0)
    .sort((a, b) => b.remainder - a.remainder || a.index - b.index)
    .forEach((part) => {
      if (remaining <= 0) {
        return
      }

      percentages[part.index] += 1
      remaining -= 1
    })

  return percentages.map(clampPercent)
}

function clampPercent(percent) {
  return Math.max(0, Math.min(Number(percent) || 0, 100))
}

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
