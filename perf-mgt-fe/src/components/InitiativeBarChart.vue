<template>
  <div ref="chartRef" class="initiative-bar-chart"></div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  categories: Array,
  values: Array,
})

const chartRef = ref(null)
let chart = null

const initChart = () => {
  if (!chartRef.value) return

  chart = echarts.init(chartRef.value)

  const option = {
    xAxis: {
      type: 'category',
      data: props.categories || [],
    },
    yAxis: { type: 'value' },
    series: [
      {
        data: props.values,
        type: 'bar',
      },
    ],
  }

  chart.setOption(option)
}

// Re-render chart if props change
// watch(() => [props.categories, props.values], () => {
//   initChart()
// })

onMounted(() => {
  initChart()

  // Optional: responsive chart
  window.addEventListener('resize', () => chart.resize())
})

onBeforeUnmount(() => {
  chart?.dispose()
})
</script>
