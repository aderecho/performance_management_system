<template>
  <div class="q-pa-md">
    <PageComboHeader
      :title="dashboardTitle"
      :breadcrumbs="[
        { label: 'Home', to: '/admin/dashboard' },
        { label: 'Dashboards' },
        { label: dashboardTitle },
      ]"
      :show-filter="false"
    />

    <q-skeleton
      v-if="dashboardEmbedStore.loading.list && !dashboard"
      type="rect"
      height="520px"
      class="rounded-borders"
    />

    <q-banner v-else-if="dashboardEmbedStore.error.list" class="bg-red-1 text-red-9 rounded-borders q-mb-md">
      Failed to load dashboard. Please refresh the page.
    </q-banner>

    <q-banner v-else-if="!dashboard" class="bg-red-1 text-red-9 rounded-borders q-mb-md">
      Dashboard not found.
    </q-banner>

    <div v-else class="embedded-dashboard-frame rounded-borders bg-white">
      <iframe
        :title="dashboard.name"
        :src="dashboard.src"
        frameborder="0"
        allowfullscreen
        :sandbox="dashboardSandbox"
      />
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import PageComboHeader from 'src/components/PageComboHeader.vue'
import { useDashboardEmbedStore } from 'src/stores/dashboardEmbed'
import { dashboardSandbox } from 'src/utils/dashboardEmbeds'

const route = useRoute()
const dashboardEmbedStore = useDashboardEmbedStore()

const dashboard = computed(() =>
  dashboardEmbedStore.dashboardBySlug(route.params.dashboardSlug),
)
const dashboardTitle = computed(() => dashboard.value?.name || 'Dashboard')

onMounted(() => {
  dashboardEmbedStore.fetchDashboards().catch(() => {})
})
</script>

<style scoped>
.embedded-dashboard-frame {
  height: min(78vh, 850px);
  min-height: 520px;
  overflow: hidden;
}

.embedded-dashboard-frame iframe {
  border: 0;
  height: 100%;
  width: 100%;
}
</style>
