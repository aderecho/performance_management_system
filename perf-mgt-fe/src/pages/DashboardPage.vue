<template>
    <q-page class="bg-page q-pa-md">
        <PageComboHeader
            title="Dashboard"
            :breadcrumbs="[
                { label: 'Admin' },
                { label: 'Dashboard' }
            ]"
            :show-filter="false"
        />

         <DashboardFilters
            v-model="filters"
            :sra-options="sraOptions"
            :status-options="statusOptions"
            @change="fetchDashboard"
        />

        <!-- OVERALL SUMMARY -->
        <q-card flat bordered class="bg-white shadow-1 q-mb-md rounded-4xl">
            <q-card-section class="q-pa-md">
                <div class="q-mb-md">
                    <div class="text-h6 text-weight-bold text-dark">Overall Summary</div>
                    <div class="text-caption text-blue-grey-8">
                        Status distribution and overall implementation progress
                    </div>
                </div>

                <q-skeleton
                    v-if="pmeStore.loading && !pmeStore.dashboardSummary"
                    type="rect"
                    height="260px"
                    class="rounded-borders"
                />

                <div v-else class="row q-col-gutter-md items-stretch">
                    <div class="col-12 col-lg-5">
                        <StatusDistributionCard
                            :total="measuresTotal"
                            :items="statusItems"
                            center-label="Measures"
                            class="rounded-3xl"
                        />
                    </div>

                    <div class="col-12 col-lg-4">
                        <div class="row q-col-gutter-sm">
                            <div
                                v-for="metric in metrics"
                                :key="metric.label"
                                class="col-12 col-sm-6"
                            >
                                <q-card
                                    flat
                                    bordered
                                    class="bg-white rounded-3xl overflow-hidden"
                                    style="min-height: 150px; border-radius: 16px;"
                                >
                                    <div
                                        style="height: 4px; background: linear-gradient(90deg, #2563eb 0%, #14b8a6 56%, #22c55e 100%)"
                                    ></div>

                                    <q-card-section class="q-pa-md">
                                        <div class="text-h3 text-weight-bold text-dark">
                                            {{ metric.value }}
                                        </div>
                                        <div class="text-caption text-blue-grey-8 q-mt-sm">
                                            {{ metric.label }}
                                        </div>
                                    </q-card-section>
                                </q-card>
                            </div>
                        </div>
                    </div>

                    <div class="col-12 col-lg-3">
                        <ProgressGauge
                            :value="overallProgress"
                            label="Overall Progress"
                            chart-width="240px"
                            chart-height="180px"
                            label-width="220px"
                            label-margin-top="-40px"
                        />
                    </div>
                </div>
            </q-card-section>
        </q-card>


        <!-- OBJECTIVE SUMMARY -->
        <q-card flat bordered class="bg-white shadow-1 rounded-4xl q-mb-md">
            <q-card-section class="q-pa-md">
                <div class="q-mb-md">
                    <div class="text-h6 text-weight-bold text-dark">Objective Summary</div>
                    <div class="text-caption text-blue-grey-8">
                        Search and filter objectives by SRA or implementation status
                    </div>
                </div>

                <q-skeleton
                    v-if="pmeStore.loading && !objectives.length"
                    type="rect"
                    height="220px"
                    class="rounded-borders"
                />

                <div
                    v-else-if="!objectives.length"
                    class="text-center text-blue-grey-7 q-py-xl"
                >
                    No objectives found.
                </div>

                <div v-else class="row q-col-gutter-md">
                    <div
                        v-for="objective in objectives"
                        :key="objective.id"
                        class="col-12 col-lg-6"
                    >
                        <q-card
                            flat
                            bordered
                            class="bg-white rounded-3xl full-height"
                            style="min-height: 294px"
                        >
                            <q-card-section class="q-pa-md">
                                <div class="row items-center justify-between no-wrap q-mb-sm">
                                    <div class="q-pr-md" style="min-width: 0">
                                        <div class="text-subtitle1 text-weight-bold text-dark">
                                            Objective {{ objective.code }}: {{ objective.name }}
                                        </div>
                                        <div class="text-caption text-blue-grey-8 text-weight-medium">
                                            {{ objective.sra?.label || 'No SRA' }}
                                        </div>
                                    </div>

                                    <div
                                        class="relative-position overflow-hidden text-center text-white text-weight-bolder"
                                        style="width: 118px; height: 26px; border-radius: 999px; background: #e5e7eb; font-size: 12px; line-height: 26px; flex: 0 0 auto"
                                    >
                                        <div
                                            class="absolute-left absolute-top"
                                            :style="{
                                                width: `${objective.progress}%`,
                                                height: '100%',
                                                background: '#2563eb'
                                            }"
                                        ></div>
                                        <span class="relative-position">{{ objective.progress }}%</span>
                                    </div>
                                </div>

                                <div class="row q-col-gutter-md items-center">
                                    <!-- STATUS DISTRIBUTION CARD -->
                                    <div class="col-12 col-sm-3 row justify-center">
                                        <div
                                            class="relative-position"
                                            :style="donutStyle(objective)"
                                        >
                                            <div
                                                class="absolute-center bg-white"
                                                style="width: 80px; height: 80px; border-radius: 50%"
                                            ></div>
                                            <div class="absolute-full column flex-center text-center">
                                                <strong
                                                    class="text-dark text-weight-bolder"
                                                    style="font-size: 24px; line-height: 1"
                                                >
                                                    {{ objective.progress }}%
                                                </strong>
                                                <span
                                                    class="text-blue-grey-8 text-weight-bolder"
                                                    style="font-size: 11px"
                                                >
                                                    Progress
                                                </span>
                                            </div>
                                        </div>
                                    </div>

                                    <div class="col-12 col-sm">
                                        <div class="row items-center justify-between q-mb-sm" style="gap: 8px; border-bottom: 1px dashed #e2e8f0">
                                            <div>
                                                <div class="text-h6 text-weight-bold text-dark">
                                                    {{ objective.main_status_label }}
                                                </div>
                                                <div class="text-caption text-blue-grey-8">
                                                    {{ objective.measure_count }} performance measure(s)
                                                </div>
                                            </div>

                                            <q-chip
                                                dense
                                                text-color="white"
                                                class="q-pa-sm"
                                                :style="{ backgroundColor: statusColor(objective.main_status) }"
                                            >
                                                Status
                                            </q-chip>
                                        </div>

                                        <q-scroll-area style="height: 122px; padding-right: 8px">
                                            <div
                                                v-for="measure in objective.measures"
                                                :key="measure.id"
                                                class="row items-center  no-wrap q-py-xs"
                                                style="gap: 8px; border-bottom: 1px dashed #e2e8f0"
                                            >
                                                <q-chip
                                                    dense
                                                    text-color="white"
                                                    class="q-pa-sm"
                                                    :style="{ backgroundColor: statusColor(measure.status) }"
                                                >
                                                    {{ measure.status_label }}
                                                </q-chip>

                                                <span
                                                    class="text-dark"
                                                    style="font-size: 13px; line-height: 1.35"
                                                >
                                                    {{ measure.code }} {{ measure.name }}
                                                </span>
                                            </div>
                                        </q-scroll-area>
                                    </div>
                                </div>
                            </q-card-section>
                        </q-card>
                    </div>
                </div>
            </q-card-section>
        </q-card>

        <!-- DETAILED OBJECTIVE LIST -->
        <q-card flat bordered class="bg-white shadow-1 rounded-3xl">
            <q-card-section class="q-pa-md">
                <div class="q-mb-md">
                    <div class="text-h6 text-weight-bold text-dark">Detailed Objective List</div>
                    <div class="text-caption text-blue-grey-8">
                        Tabular summary for reporting and validation
                    </div>
                </div>

                <AppTable
                    
                    :rows="objectives"
                    :columns="detailColumns"
                    row-key="id"
                    :show-search="false"
                >
                    <template #body-cell-main_status="props">
                        <q-td :props="props">
                            <q-chip
                                dense
                                size="md"
                                text-color="white"
                                class="text-weight-bold q-pa-sm"
                                :style="{ backgroundColor: statusColor(props.row.main_status)}"
                            >
                                {{ props.row.main_status_label }}
                            </q-chip>
                        </q-td>
                    </template>
                </AppTable>
            </q-card-section>
        </q-card>
    </q-page>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { usePmeStore } from 'src/stores/pme'
import PageComboHeader from 'src/components/PageComboHeader.vue'
import DashboardFilters from 'src/components/dashboard/DashboardFilters.vue'
import StatusDistributionCard from 'src/components/dashboard/StatusDistributionCard.vue'
import ProgressGauge from 'src/components/dashboard/ProgressGauge.vue'
import AppTable from 'src/components/admin/MarkupTable.vue'

const pmeStore = usePmeStore()

const filters = ref({
    search: null,
    sra: null,
    status: null
})

const statusConfig = [
    { key: 'on_track', label: 'On Track', color: '#22c55e' },
    { key: 'major_disruption', label: 'Major Disruption', color: '#ef4444' },
    { key: 'completed', label: 'Completed', color: '#2563eb' },
    { key: 'no_update', label: 'No Update', color: '#9ca3af' }
]

const summary = computed(() => pmeStore.dashboardSummary || {})
const objectives = computed(() => summary.value.objectives_list || [])
const sraOptions = computed(() => summary.value.sra_options || [])
const statusOptions = computed(() => (
    summary.value.status_options || statusConfig.map(item => ({
        value: item.key,
        label: item.label
    }))
))

const measuresTotal = computed(() => summary.value.measures || 0)
const overallProgress = computed(() => Math.round(summary.value.overall_progress || 0))

const statusItems = computed(() => {
    const statusCounts = summary.value.status_counts || summary.value

    return statusConfig.map(item => ({
        ...item,
        value: statusCounts[item.key] || 0
    }))
})

const metrics = computed(() => [
    { label: 'Objectives', value: summary.value.objectives || 0 },
    { label: 'Performance Measures', value: summary.value.performance_measures || 0 },
    {
        label: 'Completed / On Track',
        value: (summary.value.completed || 0) + (summary.value.on_track || 0)
    },
    { label: 'Need Attention', value: summary.value.major_disruption || 0 }
])

const detailColumns = [
    {
        name: 'objective',
        label: 'Objective',
        field: row => `${row.code} ${row.name}`,
        align: 'left'
    },
    {
        name: 'sra',
        label: 'SRA',
        field: row => row.sra?.label || 'No SRA',
        align: 'left'
    },
    {
        name: 'measure_count',
        label: 'Measures',
        field: 'measure_count',
        align: 'left'
    },
    {
        name: 'progress',
        label: 'Progress',
        field: row => `${row.progress}%`,
        align: 'left'
    },
    {
        name: 'main_status',
        label: 'Main Status',
        field: 'main_status_label',
        align: 'left'
    }
]

function statusColor(status) {
    return statusConfig.find(item => item.key === status)?.color || '#9ca3af'
}

function donutStyle(objective) {
    const progress = Math.max(0, Math.min(objective.progress || 0, 100))

    return {
        width: '124px',
        height: '124px',
        borderRadius: '50%',
        background: `conic-gradient(${statusColor(objective.main_status)} 0% ${progress}%, #e5e7eb ${progress}% 100%)`
    }
}

function fetchDashboard(nextFilters = filters.value) {
    pmeStore.fetchDashboardSummary({
        search: nextFilters.search || undefined,
        sra: nextFilters.sra || undefined,
        status: nextFilters.status || undefined
    })
}

onMounted(() => {
    fetchDashboard()
})
</script>
