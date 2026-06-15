<template>
    <q-card flat bordered class="bg-white rounded-borders full-height">
        <q-card-section class="q-pa-lg column items-center justify-center" :style="{ minHeight: cardMinHeight }">
            <div ref="chartRef" class="full-width" :style="{ maxWidth: chartWidth, height: chartHeight }"></div>

            <div class="row justify-between full-width text-blue-grey-5 text-caption"
                :style="{ maxWidth: labelWidth, marginTop: labelMarginTop }">
                <span>{{ min }}</span>
                <span>{{ max }}</span>
            </div>
        </q-card-section>
    </q-card>
</template>

<script setup>
import { nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
    value: { type: Number, default: 0 },
    label: { type: String, default: 'Overall Progress' },
    min: { type: Number, default: 0 },
    max: { type: Number, default: 100 },
    chartWidth: { type: String, default: '240px' },
    chartHeight: { type: String, default: '180px' },
    labelWidth: { type: String, default: '220px' },
    labelMarginTop: { type: String, default: '-40px' },
    cardMinHeight: { type: String, default: '292px' }
})

const chartRef = ref(null)
let chart = null

function renderChart() {
    if (!chartRef.value) return

    if (!chart) {
        chart = echarts.init(chartRef.value)
    }

    const value = Math.max(props.min, Math.min(props.value, props.max))

    chart.setOption({
        series: [
            {
                type: 'gauge',
                min: props.min,
                max: props.max,
                startAngle: 180,
                endAngle: 0,
                radius: '120%',
                center: ['50%', '70%'],
                progress: {
                    show: true,
                    roundCap: true,
                    width: 30,
                    itemStyle: {
                        color: '#2563eb'
                    }
                },
                axisLine: {
                    roundCap: true,
                    lineStyle: {
                        width: 30,
                        color: [[1, '#e5e7eb']]
                    }
                },
                pointer: { show: false },
                axisTick: { show: false },
                splitLine: { show: false },
                axisLabel: { show: false },
                detail: {
                    valueAnimation: true,
                    offsetCenter: [0, '-18%'],
                    color: '#0f172a',
                    fontSize: 36,
                    fontWeight: 800,
                    formatter: '{value}%'
                },
                title: {
                    offsetCenter: [0, '8%'],
                    color: '#64748b',
                    fontSize: 15,
                    fontWeight: 800
                },
                data: [
                    {
                        value,
                        name: props.label
                    }
                ]
            }
        ]
    })
}

function resizeChart() {
    chart?.resize()
}

watch(
    () => [props.value, props.label, props.min, props.max],
    async () => {
        await nextTick()
        renderChart()
    }
)

onMounted(async () => {
    await nextTick()
    renderChart()
    window.addEventListener('resize', resizeChart)
})

onBeforeUnmount(() => {
    window.removeEventListener('resize', resizeChart)
    chart?.dispose()
})
</script>