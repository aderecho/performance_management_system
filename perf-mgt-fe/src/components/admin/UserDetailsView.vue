<template>
  <!-- STATUS CHIPS -->
  <div class="row items-center gap-2 q-mb-md">
    <q-chip
      square
      class="user-status-chip"
      :class="data?.is_active ? 'user-status-chip--on' : 'user-status-chip--off'"
    >
      <component
        :is="data?.is_active ? CircleCheck : CircleSlash"
        :size="13"
        :stroke-width="2.5"
        class="q-mr-sm"
      />
      {{ data?.is_active ? 'Active' : 'Inactive' }}
    </q-chip>

    
  </div>

  <!-- INFO TILES -->
  <div class="row q-col-gutter-sm">
    <div class="col-12 col-sm-6">
      <div class="info-tile">
        <span class="info-tile__icon"><Mail :size="16" :stroke-width="2" /></span>
        <div class="min-w-0">
          <div class="info-tile__label">Email</div>
          <div class="info-tile__value ellipsis">{{ data?.email || '—' }}</div>
        </div>
      </div>
    </div>

    <div class="col-12 col-sm-6">
      <div class="info-tile">
        <span class="info-tile__icon"><Building2 :size="16" :stroke-width="2" /></span>
        <div class="min-w-0">
          <div class="info-tile__label">Primary unit</div>
          <div class="info-tile__value ellipsis">{{ data?.primary_unit || '—' }}</div>
        </div>
      </div>
    </div>

    <div class="col-12 col-sm-6">
      <div class="info-tile">
        <span class="info-tile__icon"><CalendarPlus :size="16" :stroke-width="2" /></span>
        <div class="min-w-0">
          <div class="info-tile__label">Member since</div>
          <div class="info-tile__value ellipsis">{{ formatDate(data?.created_at) }}</div>
        </div>
      </div>
    </div>

    <div class="col-12 col-sm-6">
      <div class="info-tile">
        <span class="info-tile__icon"><Clock :size="16" :stroke-width="2" /></span>
        <div class="min-w-0">
          <div class="info-tile__label">Last updated</div>
          <div class="info-tile__value ellipsis">{{ formatDate(data?.updated_at) }}</div>
        </div>
      </div>
    </div>
  </div>

  <!-- ROLES -->
  <div class="roles-panel q-mt-md">
    <div class="roles-panel__head">
      <ShieldCheck :size="15" :stroke-width="2" class="text-primary" />
      <span class="roles-panel__title">Assigned roles</span>
      <q-chip dense square color="grey-2" text-color="grey-8" class="q-ml-auto">
        {{ roles.length }}
      </q-chip>
    </div>

    <div v-if="roles.length" class="roles-panel__chips">
      <q-chip
        v-for="role in roles"
        :key="role"
        dense
        color="blue-1"
        text-color="blue-9"
        class="text-weight-medium"
      >
        {{ role }}
      </q-chip>
    </div>

    <div v-else class="roles-panel__empty">
      <ShieldOff :size="22" :stroke-width="1.5" />
      <span class="q-mt-xs text-caption">No roles assigned to this user.</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import {
  Mail,
  Building2,
  CalendarPlus,
  Clock,
  ShieldCheck,
  ShieldOff,
  CircleCheck,
  CircleSlash,
} from 'lucide-vue-next'
import { useRoleStore } from 'src/stores/role'

const props = defineProps({
  data: Object,
})

const roleStore = useRoleStore()
const roles = computed(() => roleStore.roleNamesByIds(props.data?.role_ids))

function formatDate(val) {
  if (!val) return '—'
  const date = new Date(val)
  if (Number.isNaN(date.getTime())) return '—'
  return date.toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' })
}
</script>
