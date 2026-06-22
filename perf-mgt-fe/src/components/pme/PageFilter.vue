<style>
.bg-card {
  min-width: 280px;
  max-width: 320px;
}
</style>

<template>
  <q-btn icon="filter_alt" color="secondary">
    <q-menu anchor="bottom right" self="top right">
      <q-card class="bg-card">

        <q-form @submit.prevent="applyFilter">

          <!-- Header -->
          <q-card-section>
            <div class="text-h6">Filter</div>
            <div class="text-caption text-grey">
              By default, items shown are based on user's unit
            </div>
          </q-card-section>

          <!-- Hierarchy -->
          <q-card-section class="q-gutter-sm">

            <div
              v-for="(level, index) in levels"
              :key="index"
            >
              <q-select
                v-model="selected[index]"
                :options="level.options"
                :label="`Level ${index + 1}`"
                :option-label="optionLabel"
                option-value="id"
                emit-value
                map-options
                dense
                outlined
                clearable
                @update:model-value="onSelect(index)"
              />
            </div>

            <q-toggle
              v-model="show_all"
              dense
              label="Show all"
            />

          </q-card-section>

          <!-- Actions -->
          <q-card-section class="row justify-end">
            <q-btn
              type="submit"
              label="Apply Filter"
              color="primary"
              dense
            />
          </q-card-section>

        </q-form>

      </q-card>
    </q-menu>
  </q-btn>
</template>
<script setup>
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { usePmeDocumentStore } from 'src/stores/pme/pmeDocument'
import { notify } from 'src/utils/notify'

const route = useRoute()
const pmeDocumentStore = usePmeDocumentStore()
const emit = defineEmits(['apply'])

const show_all = ref(false)

const levels = ref([])
const selected = ref([])

// Load hierarchy level
async function loadLevel(documentId, parentId = null, levelIndex = 0) {
  try {
    const options = await pmeDocumentStore.fetchFilterItems(documentId, parentId)

    if (!options.length) return

    levels.value[levelIndex] = { options }

  } catch {
    notify.negative('Failed to load filter items. Please try again.')
  }
}


function onSelect(levelIndex) {
  const selectedId = selected.value[levelIndex]
  const documentId = route.params.documentId

  // Remove deeper levels
  levels.value = levels.value.slice(0, levelIndex + 1)
  selected.value = selected.value.slice(0, levelIndex + 1)

  if (selectedId) {
    loadLevel(documentId, selectedId, levelIndex + 1)
  }
}

// Apply filter
function applyFilter() {
  const deepestSelected =
    selected.value[selected.value.length - 1] || null

  emit('apply', {
    item: deepestSelected,
    show_all: show_all.value
  })
}

// Format option label
function optionLabel(option) {
  if (!option) return ''
  return `${option.code} ${option.name}`
}

// Watch document change
watch(
  () => route.params.documentId,
  (newId) => {
    if (newId) {
      // Reset hierarchy state
      levels.value = []
      selected.value = []
      loadLevel(newId, null, 0)
    }
  },
  { immediate: true }
)
</script>
