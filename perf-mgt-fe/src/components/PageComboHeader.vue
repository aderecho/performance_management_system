<template>
  <div class="q-mb-lg">
    <div class="flex items-center justify-between q-mb-xs">
      
      <!-- Breadcrumbs -->
      <div>
        <div class="text-h5 text-weight-bold">
          <slot name="title">
            {{ title }}
          </slot>
        </div>

        <q-breadcrumbs class="text-grey-7 q-mt-xs">
          <q-breadcrumbs-el
            v-for="(bc, index) in breadcrumbs"
            :key="index"
            :to="bc.to"
          >
            <slot :name="`breadcrumb-${index}`" :breadcrumb="bc">
              {{ bc.label }}
            </slot>
          </q-breadcrumbs-el>
        </q-breadcrumbs>
      </div>

      <!-- Buttons -->
      <div class="flex items-center">
        
        <!-- CUSTOM SLOT (OVERRIDE ALL BUTTONS IF NEEDED) -->
        <slot name="buttons" :buttons="buttons">
          
          <!-- DEFAULT BUTTON RENDERING -->
          <template v-for="(btn, index) in buttons" :key="index">
            <q-btn
              class="q-mr-sm"
              :icon="btn.icon"
              :label="$q.screen.lt.sm ? '' : btn.label"
              :color="btn.color || 'primary'"
              :flat="btn.flat ?? false"
              :outline="btn.outline ?? false"
              :dense="btn.dense ?? false"
              :loading="btn.loading ?? false"
              :disable="btn.disable ?? false"
              v-if="!btn.permission || btn.permission()"
              @click="btn.onClick"
            >
              <q-tooltip v-if="btn.tooltip">
                {{ btn.tooltip }}
              </q-tooltip>
            </q-btn>
          </template>

        </slot>

        <!-- Filter -->
        <PageFilter v-if="showFilter" @apply="forwardFilter" />

      </div>
    </div>

    <q-separator spaced />
  </div>
</template>

<script setup>
import PageFilter from 'src/components/pme/PageFilter.vue';

const emit = defineEmits(['apply'])

function forwardFilter(filters) {
  emit('apply', filters)
}

defineProps({
  title: {
    type: String,
    required: true
  },
  breadcrumbs: {
    type: Array,
    default: () => []
  },
  buttons: {
    type: Array,
    default: () => []
  },
  showFilter: {
    type: Boolean,
    default: true
  }
})
</script>

<style scoped>
.text-h5 {
  font-weight: 600;
}
</style>