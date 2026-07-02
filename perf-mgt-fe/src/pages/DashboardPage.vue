<template>
  <q-page class="bg-page q-pa-md">
    <PageComboHeader
      title="Performance Dashboard"
      :breadcrumbs="[
        { label: 'Admin' }, 
        { label: 'Dashboard' }
      ]"
      :show-filter="false"
    />

    <DashboardFilters
      v-model="filters"
      :show-search="false"
      :select-filters="dashboardFilterFields"
      @change="fetchDashboard"
    />

    <!-- OVERALL SUMMARY -->
    <q-card flat bordered class="bg-white shadow-1 q-mb-md rounded-4xl">
      <q-card-section class="q-pa-md">
        <div class="q-mb-md">
          <div class="text-h6 text-weight-bold text-dark">
            <template v-if="selectedTemplateLabel">
              Overall <span class="text-primary">{{ selectedTemplateLabel }}</span> Summary
            </template>
            <template v-else>Overall Summary</template>
          </div>
          <div class="text-caption text-blue-grey-8">
            Status distribution and overall implementation progress
          </div>
        </div>

        <q-skeleton
          v-if="dashboardStore.loading && !dashboardStore.dashboardSummary"
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
              <div v-for="metric in metrics" :key="metric.label" class="col-12 col-sm-6">
                <q-card
                  flat
                  bordered
                  class="bg-white rounded-3xl overflow-hidden rounded-3xl min-h-150"
                >
                  <div class="h-1 bg-gradient-primary-ocean"></div>

                  <q-card-section class="q-pa-md">
                    <div class="text-3xl text-weight-bold text-dark">
                      {{ metric.value }}
                    </div>
                    <div class="text-caption text-grey-8 q-mt-sm">
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

    <!-- DOCUMENT SUMMARY -->
    <q-card flat bordered class="bg-white shadow-1 rounded-4xl q-mb-md">
      <q-card-section class="q-pa-md">
        <div class="q-mb-md">
          <div class="text-h6 text-weight-bold text-dark">{{ cardSummaryTitle }}</div>
          <div class="text-caption text-blue-grey-8">
            Filter {{ cardLabelPluralLower }} by {{ groupFilterLabel }} or implementation status
          </div>
        </div>

        <q-skeleton
          v-if="dashboardStore.loading && !objectives.length"
          type="rect"
          height="220px"
          class="rounded-borders"
        />

        <div v-else-if="!objectives.length" class="text-center text-blue-grey-7 q-py-xl">
          No {{ cardLabelPluralLower }} found.
        </div>

        <div v-else class="row q-col-gutter-md">
          <div v-for="objective in objectives" :key="objective.id" class="col-12 col-lg-6">
            <q-card flat bordered class="bg-white rounded-3xl full-height min-h-294">
              <q-card-section class="q-pa-md">
                <div class="row items-center justify-between no-wrap q-mb-sm">
                  <div class="q-pr-md min-w-0">
                    <div class="text-subtitle1 text-weight-bold text-dark">
                      {{ objective.code }}: {{ objective.name }}
                    </div>
                    <div class="text-caption text-blue-grey-8 text-weight-medium">
                      {{ objective.group?.label || `No ${groupFilterLabel}` }}
                    </div>
                  </div>

                  <div
                    class="relative-position overflow-hidden text-center text-white text-weight-bolder w-30 h-7 rounded-full bg-grey text-xs leading-26 flex-none"
                  >
                    <div
                      class="absolute-left absolute-top dashboard-progress-fill"
                      :style="progressFillStyle(objective.progress)"
                    ></div>
                    <span class="relative-position">{{ objective.progress }}%</span>
                  </div>
                </div>

                <div class="row q-col-gutter-md items-center">
                  <!-- STATUS DISTRIBUTION CARD -->
                  <div class="col-12 col-sm-3 row justify-center">
                    <StatusDistributionCard
                      variant="inline"
                      :show-legend="false"
                      :total="100"
                      :items="objectiveProgressItems(objective)"
                      :center-value="clampProgress(objective.progress)"
                      center-suffix="%"
                      center-label="Progress"
                      donut-size="124px"
                      inner-circle-size="80px"
                      min-height="124px"
                      center-value-class="text-dark text-weight-bolder text-2xl leading-none"
                      center-label-class="text-blue-grey-8 text-weight-bolder text-2xs"
                    />
                  </div>

                  <div class="col-12 col-sm">
                    <div
                      class="row items-center justify-between q-mb-sm gap-2 border-b border-dashed border-slate-200"
                    >
                      <div>
                        <div class="text-h6 text-weight-bold text-dark">
                          {{ objective.main_status_label }}
                        </div>
                        <div class="text-caption text-blue-grey-8">
                          {{ objective.measure_count }} {{ measureCountLabel(objective.measure_count) }}
                        </div>
                      </div>

                      <q-chip
                        dense
                        text-color="white"
                        class="q-pa-sm"
                        :class="statusClass(objective.main_status)"
                      >
                        Status
                      </q-chip>
                    </div>

                    <q-scroll-area class="h-122 pr-2">
                      <div
                        v-for="measure in objective.measures"
                        :key="measure.id"
                        class="row items-center no-wrap q-py-xs gap-2 border-b border-dashed border-slate-200"
                      >
                        <q-chip
                          dense
                          text-color="white"
                          class="q-pa-sm"
                          :class="statusClass(measure.status)"
                        >
                          {{ measure.status_label }}
                        </q-chip>

                        <span class="text-dark text-13 leading-snug">
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
          <div class="text-h6 text-weight-bold text-dark">Detailed {{ cardLabel }} List</div>
          <div class="text-caption text-blue-grey-8">
            Tabular summary for reporting and validation
          </div>
        </div>

        <AppTable :rows="objectives" :columns="detailColumns" row-key="id" :show-search="false">
          <template #body-cell-main_status="props">
            <q-td :props="props">
              <q-chip
                dense
                size="md"
                text-color="white"
                class="text-weight-bold q-pa-sm"
                :class="statusClass(props.row.main_status)"
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
import { useDashboardStore } from 'src/stores/pme/dashboard'
import PageComboHeader from 'src/components/PageComboHeader.vue'
import DashboardFilters from 'src/components/dashboard/DashboardFilters.vue'
import StatusDistributionCard from 'src/components/dashboard/StatusDistributionCard.vue'
import ProgressGauge from 'src/components/dashboard/ProgressGauge.vue'
import AppTable from 'src/components/admin/MarkupTable.vue'
import { notify } from 'src/utils/notify'

const dashboardStore = useDashboardStore()

const filters = ref({
  template: null,
  document: null,
  group: null,
  status: null,
})
const lastTemplate = ref(filters.value.template)
const lastDocument = ref(filters.value.document)

const statusConfig = [
  { key: 'on_track', label: 'On Track', color: '#22c55e' },
  { key: 'major_disruption', label: 'Major Disruption', color: '#ef4444' },
  { key: 'completed', label: 'Completed', color: '#2563eb' },
  { key: 'no_update', label: 'No Update', color: '#9ca3af' },
]

const summary = computed(() => dashboardStore.dashboardSummary || {})
const objectives = computed(() => summary.value.objectives_list || [])
const templateOptions = computed(() => summary.value.template_options || [])
const documentOptions = computed(() => {
  const options = summary.value.document_options || []

  if (!filters.value.template) {
    return options
  }

  return options.filter((option) => option.template === filters.value.template)
})
const groupOptions = computed(() => summary.value.group_options || summary.value.sra_options || [])
const groupFilterLabel = computed(() => summary.value.group_filter_label || 'Strategic Result Area')
const cardLabel = computed(() => summary.value.card_label || 'Objective')
const measureLabel = computed(() => summary.value.measure_label || 'Performance Measure')
const cardLabelPlural = computed(() => pluralize(cardLabel.value))
const cardLabelPluralLower = computed(() => cardLabelPlural.value.toLowerCase())
const measureLabelPlural = computed(() => pluralize(measureLabel.value))
const selectedTemplateLabel = computed(() => optionLabel(templateOptions.value, filters.value.template))
const cardSummaryTitle = computed(() => `${cardLabel.value} Summary`)
const statusOptions = computed(
  () =>
    summary.value.status_options ||
    statusConfig.map((item) => ({
      value: item.key,
      label: item.label,
    })),
)
const dashboardFilterFields = computed(() => [
  {
    name: 'template',
    label: 'Template',
    options: templateOptions.value,
    colClass: 'col-12 col-md-3',
  },
  {
    name: 'document',
    label: 'Document',
    options: documentOptions.value,
    colClass: 'col-12 col-md-3',
  },
  {
    name: 'group',
    label: groupFilterLabel.value,
    options: groupOptions.value,
    colClass: 'col-12 col-md-3',
  },
  {
    name: 'status',
    label: 'Status',
    options: statusOptions.value,
    colClass: 'col-12 col-md-3',
  },
])

const measuresTotal = computed(() => summary.value.measures || 0)
const overallProgress = computed(() => Math.round(summary.value.overall_progress || 0))

const statusItems = computed(() => {
  const statusCounts = summary.value.status_counts || summary.value

  return statusConfig.map((item) => ({
    ...item,
    value: statusCounts[item.key] || 0,
  }))
})

const metrics = computed(() => [
  { label: cardLabelPlural.value, value: summary.value.objectives || 0 },
  { label: measureLabelPlural.value, value: summary.value.performance_measures || 0 },
  { label: 'Completed / On Track', value: (summary.value.completed || 0) + (summary.value.on_track || 0) },
  { label: 'Need Attention', value: summary.value.major_disruption || 0 },
])

const detailColumns = computed(() => [
  {
    name: 'objective',
    label: cardLabel.value,
    field: (row) => `${row.code} ${row.name}`,
    align: 'left',
  },
  {
    name: 'group',
    label: groupFilterLabel.value,
    field: (row) => row.group?.label || `No ${groupFilterLabel.value}`,
    align: 'left',
  },
  {
    name: 'measure_count',
    label: measureLabelPlural.value,
    field: 'measure_count',
    align: 'left',
  },
  {
    name: 'progress',
    label: 'Progress',
    field: (row) => `${row.progress}%`,
    align: 'left',
  },
  {
    name: 'main_status',
    label: 'Main Status',
    field: 'main_status_label',
    align: 'left',
  },
])

function pluralize(label) {
  if (!label) {
    return ''
  }

  return label.endsWith('s') ? label : `${label}s`
}

function optionLabel(options, value) {
  if (!value) {
    return ''
  }

  return options.find((option) => option.value === value)?.label || ''
}

function measureCountLabel(count) {
  return (Number(count) === 1 ? measureLabel.value : measureLabelPlural.value).toLowerCase()
}

function statusColor(status) {
  return statusConfig.find((item) => item.key === status)?.color || '#9ca3af'
}

function statusClass(status) {
  return `bg-status-${statusConfig.find((item) => item.key === status)?.key || 'default'}`
}

function clampProgress(progress) {
  return Math.max(0, Math.min(Number(progress) || 0, 100))
}

function progressFillStyle(progress) {
  const width = clampProgress(progress)

  return {
    '--dashboard-progress-width': `${width}%`,
  }
}

function objectiveProgressItems(objective) {
  return [
    {
      key: 'progress',
      label: 'Progress',
      color: statusColor(objective.main_status),
      value: clampProgress(objective.progress),
    },
  ]
}

async function fetchDashboard(nextFilters = filters.value) {
  const nextTemplate = nextFilters.template || null
  const templateChanged = nextTemplate !== lastTemplate.value
  const nextDocument = templateChanged ? null : nextFilters.document || null
  const documentChanged = nextDocument !== lastDocument.value
  const selectedGroup = templateChanged || documentChanged ? null : nextFilters.group

  if (templateChanged || nextDocument !== nextFilters.document || selectedGroup !== nextFilters.group) {
    filters.value = {
      ...nextFilters,
      document: nextDocument,
      group: selectedGroup,
    }
  }

  try {
    await dashboardStore.fetchDashboardSummary({
      template: nextTemplate || undefined,
      document: nextDocument || undefined,
      group: selectedGroup || undefined,
      status: nextFilters.status || undefined,
    })
    lastTemplate.value = nextTemplate
    lastDocument.value = nextDocument
  } catch {
    notify.negative('Failed to load dashboard summary. Please try again.')
  }
}

onMounted(() => {
  fetchDashboard()
})
</script>
