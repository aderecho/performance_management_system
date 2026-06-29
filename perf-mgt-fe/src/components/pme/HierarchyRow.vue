<template>
  <tr
    class="hierarchy-row"
    :class="rowClasses"
    :role="isInteractive ? 'button' : null"
    :tabindex="isInteractive ? 0 : null"
    :aria-expanded="hasChildren ? expanded : null"
    @click="handleRowClick"
    @keydown.enter.prevent="handleRowClick"
    @keydown.space.prevent="handleRowClick"
  >
    <td >
      <div class="row no-wrap items-center" :style="indentStyle">
        <span class="hierarchy-toggle flex-none">
          <q-btn
            v-if="hasChildren"
            flat
            dense
            round
            size="sm"
            :aria-label="expanded ? 'Collapse section' : 'Expand section'"
            @click.stop="toggle"
          >
            <ChevronRight
              :size="16"
              class="hierarchy-chevron"
              :class="{ 'hierarchy-chevron--open': expanded }"
            />
          </q-btn>
          <span v-else class="hierarchy-leaf-dot" :class="leafDotClass" />
        </span>

        <div class="flex-1 min-w-0">
          <span v-if="item.code" class="hierarchy-code">{{ item.code }}</span>
          <div class="hierarchy-name" :class="nameClass">{{ item.name }}</div>
        </div>

        <ChevronRight v-if="isClickable" :size="16" class="hierarchy-open-hint flex-none" />
        <q-tooltip v-if="isClickable" anchor="center right" self="center left">
          View initiatives
        </q-tooltip>
      </div>
    </td>

    <template v-if="isClickable">
      <td class="text-center">
        <span class="hierarchy-target">{{ item.target }}</span>
        <span v-if="item.unit_of_measure" class="hierarchy-unit">
          {{ item.unit_of_measure.short_code }}
        </span>
      </td>
      <td class="text-center hierarchy-accomplishment">{{ item.total_accomplishment }}</td>
      <td class="text-center">
        <div class="column items-center q-gutter-y-xs">
          <q-chip outline dense :color="achievement.color" :label="`${percent}%`" class="hierarchy-pct" />
          <div class="hierarchy-progress">
            <div class="hierarchy-progress-bar" :class="achievement.barClass" :style="progressStyle" />
          </div>
        </div>
      </td>
    </template>
    <template v-else>
      <td class="text-center" colspan="3">
        <!-- <span v-if="hasChildren" class="text-2xs text-uppercase text-grey-5">
          {{ item.children.length }} {{ item.children.length === 1 ? 'item' : 'items' }}
        </span> -->
      </td>
    </template>
  </tr>

  <template v-if="hasChildren && expanded">
    <HierarchyRow
      v-for="child in item.children"
      :key="child.id"
      :item="child"
      :level="level + 1"
      :document-id="documentId"
      :document="document"
      @open-initiatives="$emit('open-initiatives', $event)"
    />
  </template>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ChevronRight } from 'lucide-vue-next'

const props = defineProps({
  item: { type: Object, required: true },
  level: { type: Number, default: 0 },
  documentId: { type: String, required: true },
  document: { type: Object, required: true }
})

const emit = defineEmits(['open-initiatives'])

const expanded = ref(true)

const hasChildren = computed(() => !!props.item.children?.length)
const isClickable = computed(() => !!props.item.target)
const isGroup = computed(() => !props.item.target)
const isInteractive = computed(() => isClickable.value || hasChildren.value)

const percent = computed(() => Math.round(Number(props.item.percent_achieved) || 0))
const isAccomplished = computed(() => percent.value >= 100)

const achievement = computed(() => {
  if (percent.value >= 100) return { color: 'positive', barClass: 'hierarchy-progress-bar--positive' }
  if (percent.value >= 50) return { color: 'warning', barClass: 'hierarchy-progress-bar--warning' }
  return { color: 'negative', barClass: 'hierarchy-progress-bar--negative' }
})

// Leaf dot doubles as a status cue on measure rows: green when accomplished,
// red when not. Non-measure leaf rows keep the neutral default.
const leafDotClass = computed(() => {
  if (!isClickable.value) return ''
  return isAccomplished.value ? 'hierarchy-leaf-dot--accomplished' : 'hierarchy-leaf-dot--pending'
})

const progressStyle = computed(() => ({ width: `${Math.min(percent.value, 100)}%` }))

const indentStyle = computed(() => ({ paddingLeft: `${props.level * 20}px` }))

const rowClasses = computed(() => ({
  'hierarchy-row--group': isGroup.value,
  'hierarchy-row--clickable': isClickable.value
}))

const nameClass = computed(() =>
  isGroup.value ? 'text-weight-semibold text-grey-9' : 'text-grey-8'
)

function toggle() {
  expanded.value = !expanded.value
}

function handleRowClick() {
  if (isClickable.value) {
    emit('open-initiatives', props.item)
  } else if (hasChildren.value) {
    toggle()
  }
}
</script>
