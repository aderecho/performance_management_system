<template>
  <q-dialog v-model="model">
    <q-card class="user-form-dialog">
      <!-- HEADER -->
      <q-card-section class="user-dialog__header row items-center no-wrap q-gutter-sm">
        <div class="user-dialog__icon">
          <component :is="isEdit ? UserRoundPen : UserRoundPlus" :size="20" :stroke-width="2" />
        </div>
        <div class="col min-w-0">
          <div class="text-h6 leading-snug">{{ isEdit ? 'Update User' : 'Create User' }}</div>
          <div class="text-caption text-grey-7">
            {{
              isEdit
                ? 'Edit account details, roles and unit assignments.'
                : 'Add a new account with roles and unit assignments.'
            }}
          </div>
        </div>
        <q-btn icon="close" flat round dense aria-label="Close" v-close-popup />
      </q-card-section>

      <q-separator />

      <!-- FORM -->
      <q-form ref="formRef" class="user-form-dialog__form" @submit.prevent="handleSubmit">
        <q-card-section class="user-form-scroll q-gutter-y-sm">
          <!-- ACCOUNT CREDENTIALS -->
          <section>
            <header class="user-section-head">
              <div>
                <div class="user-section-title">Account credentials</div>
                <div class="user-section-sub">Used to sign in to the platform.</div>
              </div>
            </header>

            <div class="row q-col-gutter-md">
              <div class="col-12 col-sm-6">
                <q-input
                  v-model.trim="form.email"
                  label="Email"
                  type="email"
                  dense
                  outlined
                  :rules="[
                    (val) => !!val || 'Email is required',
                    (val) => /.+@.+\..+/.test(val) || 'Enter a valid email',
                  ]"
                  hide-bottom-space
                >
                  <template #prepend>
                    <Mail :size="18" :stroke-width="2" class="text-grey-6" />
                  </template>
                </q-input>
              </div>

              <div class="col-12 col-sm-6">
                <q-input
                  v-model="form.password"
                  :label="isEdit ? 'New password' : 'Password'"
                  :type="showPassword ? 'text' : 'password'"
                  dense
                  outlined
                  autocomplete="new-password"
                  :hint="isEdit ? 'Leave blank to keep the current password' : ''"
                  :rules="isEdit ? [] : [(val) => !!val || 'Password is required']"
                  :hide-bottom-space="!isEdit"
                >
                  <template #prepend>
                    <KeyRound :size="18" :stroke-width="2" class="text-grey-6" />
                  </template>
                  <template #append>
                    <q-btn
                      flat
                      round
                      dense
                      size="sm"
                      :aria-label="showPassword ? 'Hide password' : 'Show password'"
                      @click="showPassword = !showPassword"
                    >
                      <component
                        :is="showPassword ? EyeOff : Eye"
                        :size="18"
                        :stroke-width="2"
                        class="text-grey-6"
                      />
                    </q-btn>
                  </template>
                </q-input>
              </div>
            </div>
          </section>

          <q-separator />

          <!-- PERSONAL DETAILS -->
          <section>
            <header class="user-section-head">
              <div>
                <div class="user-section-title">Personal details</div>
                <div class="user-section-sub">The person's legal name.</div>
              </div>
            </header>

            <div class="row q-col-gutter-md">
              <div class="col-12 col-sm-6">
                <q-input
                  v-model="form.profile.first_name"
                  label="First name"
                  dense
                  outlined
                  :rules="[(val) => !!val || 'Required']"
                  hide-bottom-space
                />
              </div>
              <div class="col-12 col-sm-6">
                <q-input
                  v-model="form.profile.middle_name"
                  label="Middle name"
                  dense
                  outlined
                  hide-bottom-space
                />
              </div>
              <div class="col-12 col-sm-6">
                <q-input
                  v-model="form.profile.last_name"
                  label="Last name"
                  dense
                  outlined
                  :rules="[(val) => !!val || 'Required']"
                  hide-bottom-space
                />
              </div>
              <div class="col-12 col-sm-6">
                <q-input
                  v-model="form.profile.suffix"
                  label="Suffix"
                  dense
                  outlined
                  hide-bottom-space
                />
              </div>
            </div>
          </section>

          <q-separator />

          <!-- ROLES & ACCESS -->
          <section>
            <header class="user-section-head">
    
              <div>
                <div class="user-section-title">Roles &amp; access</div>
                <div class="user-section-sub">Controls what this user can do.</div>
              </div>
            </header>

            <q-select
              v-model="form.role_ids"
              :options="roleStore.options"
              option-value="value"
              option-label="label"
              emit-value
              map-options
              multiple
              use-chips
              label="Roles"
              outlined
              dense
            />

            <div class="row q-col-gutter-md q-mt-xs">
              <div class="col-12 col-sm-6">
                <div
                  class="access-card"
                  :class="{ 'access-card--on': form.is_active }"
                  @click="form.is_active = !form.is_active"
                >
                  <span class="access-card__icon access-card__icon--active">
                    <UserCheck :size="18" :stroke-width="2" />
                  </span>
                  <div class="col min-w-0">
                    <div class="access-card__title">Active account</div>
                  </div>
                  <q-toggle
                    :model-value="form.is_active"
                    color="secondary"
                    aria-label="Active account"
                    @update:model-value="(val) => (form.is_active = val)"
                    @click.stop
                  />
                </div>
              </div>

              <div class="col-12 col-sm-6">
                <div
                  class="access-card"
                  :class="{ 'access-card--on-super': form.is_superuser }"
                  @click="form.is_superuser = !form.is_superuser"
                >
                  <span class="access-card__icon access-card__icon--super">
                    <BadgeCheck :size="18" :stroke-width="2" />
                  </span>
                  <div class="col min-w-0">
                    <div class="access-card__title">Superuser</div>
                  </div>
                  <q-toggle
                    :model-value="form.is_superuser"
                    color="accent"
                    aria-label="Superuser"
                    @update:model-value="(val) => (form.is_superuser = val)"
                    @click.stop
                  />
                </div>
              </div>
            </div>
          </section>

          <q-separator />

          <!-- ORGANIZATION -->
          <section>
            <header class="user-section-head">
            
              <div>
                <div class="user-section-title">Organization</div>
                <div class="user-section-sub">Assign units and the primary one.</div>
              </div>
            </header>

            <div class="row q-col-gutter-md">
              <div class="col-12 col-sm-6">
                <q-select
                  v-model="form.units"
                  v-model:input-value="unitSearch"
                  :options="filteredUnitOptions"
                  option-value="id"
                  option-label="name"
                  emit-value
                  map-options
                  multiple
                  use-chips
                  use-input
                  input-debounce="300"
                  :fill-input="false"
                  label="Units"
                  outlined
                  dense
                  @filter="filterUnits"
                  @update:model-value="onSelectUnit"
                />
              </div>

              <div class="col-12 col-sm-6">
                <q-select
                  v-model="form.primary_unit"
                  :options="filteredUnits"
                  option-value="id"
                  option-label="name"
                  emit-value
                  map-options
                  clearable
                  label="Primary unit"
                  outlined
                  dense
                  :disable="!form.units.length"
                  :hint="!form.units.length ? 'Select at least one unit first' : ''"
                />
              </div>
            </div>
          </section>
        </q-card-section>

        <q-separator />

        <q-card-actions class="user-form-actions" align="right">
          <q-btn flat label="Cancel" v-close-popup />
          <q-btn
            unelevated
            type="submit"
            color="primary"
            :label="isEdit ? 'Update' : 'Create'"
            :loading="loading"
          />
        </q-card-actions>
      </q-form>
    </q-card>
  </q-dialog>
</template>

<script setup>
import { ref, computed, onMounted, reactive, watch } from 'vue'
import { useCoreStore } from 'src/stores/core'
import { useRoleStore } from 'src/stores/role'
import {
  Mail,
  KeyRound,
  Eye,
  EyeOff,
  UserRoundPlus,
  UserRoundPen,
  UserCheck,
  BadgeCheck,
} from 'lucide-vue-next'

const coreStore = useCoreStore()
const roleStore = useRoleStore()

const props = defineProps({
  modelValue: Boolean,
  data: Object,
  loading: Boolean,
})

const emit = defineEmits(['update:modelValue', 'submit'])

const model = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
})

const isEdit = computed(() => !!props.data)
const formRef = ref(null)
const showPassword = ref(false)

// Form State
const form = reactive({
  email: '',
  password: '',
  is_active: true,
  is_superuser: false,
  role_ids: [],
  profile: {
    first_name: '',
    middle_name: '',
    last_name: '',
    suffix: '',
  },
  units: [],
  primary_unit: null,
})

const filteredUnits = computed(() => {
  return coreStore.units.filter((u) => form.units.includes(u.id))
})

// Filter units
const filteredUnitOptions = ref([])
const unitSearch = ref('')

function onSelectUnit() {
  unitSearch.value = ''
}

function filterUnits(val, update) {
  update(() => {
    const needle = val.toLowerCase()

    filteredUnitOptions.value = coreStore.units.filter(
      (unit) =>
        unit.name.toLowerCase().includes(needle) || unit.short_code?.toLowerCase().includes(needle),
    )
  })
}

// Check if data prop changes
watch(
  () => props.data,
  (val) => {
    showPassword.value = false
    formRef.value?.resetValidation()

    if (val) {
      form.email = val.email || ''
      form.password = ''
      form.is_active = val.is_active ?? false
      form.is_superuser = val.is_superuser ?? false
      form.role_ids = val.role_ids || []

      form.profile.first_name = val.profile?.first_name || ''
      form.profile.middle_name = val.profile?.middle_name || ''
      form.profile.last_name = val.profile?.last_name || ''
      form.profile.suffix = val.profile?.suffix || ''

      const units = val.user_units || []

      form.units = units.map((u) => u.unit)
      form.primary_unit = units.find((u) => u.is_primary)?.unit || null
    } else {
      resetForm()
    }
  },
  { immediate: true },
)

watch(
  () => form.units,
  (newUnits) => {
    if (!newUnits.includes(form.primary_unit)) {
      form.primary_unit = null
    }
  },
)

// Reset
function resetForm() {
  form.email = ''
  form.password = ''
  form.is_active = true
  form.is_superuser = false
  form.role_ids = []
  form.profile.first_name = ''
  form.profile.middle_name = ''
  form.profile.last_name = ''
  form.profile.suffix = ''
  form.units = []
  form.primary_unit = null
}

// Submit (q-form only fires this once validation passes)
function handleSubmit() {
  emit('submit', { ...form })
}

onMounted(async () => {
  try {
    await Promise.all([coreStore.fetchUnits(), roleStore.fetchRoles()])
  } catch {
    // Store captures the error state.
  } finally {
    filteredUnitOptions.value = coreStore.units
  }
})
</script>
