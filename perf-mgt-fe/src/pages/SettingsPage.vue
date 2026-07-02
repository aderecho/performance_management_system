<template>
  <div class="q-pa-md">
    <PageComboHeader
      title="Settings"
      :breadcrumbs="[
        { label: 'Home', to: '/admin/dashboard' },
        { label: 'Admin' },
        { label: 'Settings' },
      ]"
      :show-filter="false"
    />

    <div class="row q-col-gutter-md">
      <div class="col-12 col-lg-5">
        <q-card flat bordered class="rounded-borders">
          <q-card-section>
            <div class="text-subtitle1 text-weight-medium">Add Dashboard</div>
          </q-card-section>

          <q-separator />

          <q-banner v-if="dashboardEmbedStore.error.save" class="bg-red-1 text-red-9 q-ma-md rounded-borders">
            Failed to save dashboard. Please check the embed URL and try again.
          </q-banner>

          <q-form @submit.prevent="addDashboard">
            <q-card-section class="column q-gutter-md">
              <q-input
                v-model="form.name"
                label="Dashboard Name"
                outlined
                dense
                :rules="[(value) => !!value || 'Dashboard name is required']"
              />

              <q-input
                v-model="form.embed"
                label="Looker Studio Embed URL or iframe"
                outlined
                dense
                autogrow
                :rules="[
                  (value) => !!value || 'Embed URL or iframe is required',
                  validateEmbed,
                ]"
              />
            </q-card-section>

            <q-card-actions align="right" class="q-px-md q-pb-md">
              <q-btn
                flat
                color="grey-8"
                label="Clear"
                :disable="dashboardEmbedStore.loading.save"
                @click="resetForm"
              />
              <q-btn
                color="primary"
                label="Add Dashboard"
                type="submit"
                :loading="dashboardEmbedStore.loading.save"
              />
            </q-card-actions>
          </q-form>
        </q-card>
      </div>

      <div class="col-12 col-lg-7">
        <q-card flat bordered class="rounded-borders">
          <q-card-section>
            <div class="text-subtitle1 text-weight-medium">Embedded Dashboards</div>
          </q-card-section>

          <q-separator />

          <q-card-section v-if="dashboardEmbedStore.loading.list">
            <q-skeleton type="rect" height="72px" class="rounded-borders" />
          </q-card-section>

          <q-banner v-else-if="dashboardEmbedStore.error.list" class="bg-red-1 text-red-9 q-ma-md rounded-borders">
            Failed to load dashboards. Please refresh the page.
          </q-banner>

          <q-card-section v-else-if="!dashboardEmbedStore.dashboards.length" class="text-grey-7">
            No embedded dashboards yet.
          </q-card-section>

          <q-list v-else separator>
            <q-item v-for="dashboard in dashboardEmbedStore.dashboards" :key="dashboard.slug">
              <q-item-section>
                <q-item-label>{{ dashboard.name }}</q-item-label>
                <q-item-label caption lines="1">{{ dashboard.src }}</q-item-label>
              </q-item-section>

              <q-item-section side>
                <div class="row items-center q-gutter-xs">
                  <q-btn
                    flat
                    dense
                    round
                    icon="open_in_new"
                    :to="{ name: 'embedded-dashboard', params: { dashboardSlug: dashboard.slug } }"
                  >
                    <q-tooltip>Open dashboard</q-tooltip>
                  </q-btn>

                  <q-btn flat dense round icon="edit" @click="openEditDialog(dashboard)">
                    <q-tooltip>Edit dashboard</q-tooltip>
                  </q-btn>

                  <q-btn
                    flat
                    dense
                    round
                    color="negative"
                    icon="delete"
                    :loading="dashboardEmbedStore.loading.delete"
                    @click="removeDashboard(dashboard)"
                  >
                    <q-tooltip>Remove dashboard</q-tooltip>
                  </q-btn>
                </div>
              </q-item-section>
            </q-item>
          </q-list>
        </q-card>
      </div>
    </div>

    <q-dialog v-model="editDialog">
      <q-card class="rounded-borders edit-dashboard-card">
        <q-card-section>
          <div class="text-subtitle1 text-weight-medium">Edit Dashboard</div>
        </q-card-section>

        <q-separator />

        <q-banner v-if="dashboardEmbedStore.error.save" class="bg-red-1 text-red-9 q-ma-md rounded-borders">
          Failed to save dashboard. Please check the embed URL and try again.
        </q-banner>

        <q-form @submit.prevent="updateDashboard">
          <q-card-section class="column q-gutter-md">
            <q-input
              v-model="editForm.name"
              label="Dashboard Name"
              outlined
              dense
              :rules="[(value) => !!value || 'Dashboard name is required']"
            />

            <q-input
              v-model="editForm.embed"
              label="Looker Studio Embed URL or iframe"
              outlined
              dense
              autogrow
              :rules="[
                (value) => !!value || 'Embed URL or iframe is required',
                validateEmbed,
              ]"
            />
          </q-card-section>

          <q-card-actions align="right" class="q-px-md q-pb-md">
            <q-btn
              flat
              color="grey-8"
              label="Cancel"
              :disable="dashboardEmbedStore.loading.save"
              @click="closeEditDialog"
            />
            <q-btn
              color="primary"
              label="Save Changes"
              type="submit"
              :loading="dashboardEmbedStore.loading.save"
            />
          </q-card-actions>
        </q-form>
      </q-card>
    </q-dialog>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import PageComboHeader from 'src/components/PageComboHeader.vue'
import { useDashboardEmbedStore } from 'src/stores/dashboardEmbed'
import { extractDashboardSrc } from 'src/utils/dashboardEmbeds'
import { notify } from 'src/utils/notify'

const dashboardEmbedStore = useDashboardEmbedStore()
const form = ref({
  name: '',
  embed: '',
})
const editDialog = ref(false)
const selectedDashboard = ref(null)
const editForm = ref({
  name: '',
  embed: '',
})

function validateEmbed(value) {
  return (
    !!extractDashboardSrc(value || '') ||
    'Use a Looker Studio embed URL or iframe from lookerstudio.google.com.'
  )
}

function resetForm() {
  form.value = {
    name: '',
    embed: '',
  }
}

function openEditDialog(dashboard) {
  selectedDashboard.value = dashboard
  editForm.value = {
    name: dashboard.name || '',
    embed: dashboard.src || '',
  }
  editDialog.value = true
}

function closeEditDialog() {
  editDialog.value = false
  selectedDashboard.value = null
  editForm.value = {
    name: '',
    embed: '',
  }
}

async function addDashboard() {
  const name = form.value.name.trim()
  const src = extractDashboardSrc(form.value.embed)

  if (!name || !src) {
    return
  }

  try {
    await dashboardEmbedStore.createDashboard({ name, src })
    resetForm()
    notify.positive('Dashboard added.')
  } catch {
    notify.negative('Failed to add dashboard.')
  }
}

async function removeDashboard(dashboard) {
  try {
    await dashboardEmbedStore.deleteDashboard(dashboard.id)
    notify.positive('Dashboard removed.')
  } catch {
    notify.negative('Failed to remove dashboard.')
  }
}

async function updateDashboard() {
  const name = editForm.value.name.trim()
  const src = extractDashboardSrc(editForm.value.embed)

  if (!selectedDashboard.value || !name || !src) {
    return
  }

  try {
    await dashboardEmbedStore.updateDashboard(selectedDashboard.value.id, { name, src })
    closeEditDialog()
    notify.positive('Dashboard updated.')
  } catch {
    notify.negative('Failed to update dashboard.')
  }
}

onMounted(() => {
  dashboardEmbedStore.fetchDashboards().catch(() => {})
})
</script>

<style scoped>
.edit-dashboard-card {
  width: min(560px, 92vw);
}
</style>
