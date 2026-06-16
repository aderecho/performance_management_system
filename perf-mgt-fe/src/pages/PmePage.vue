<template>
    <q-page class="flex q-pa-lg">
        <div class="full-width">


            <PageComboHeader :title="pmeStore.documentWithItems.template_name || ''"
            :breadcrumbs="[
                { label: 'Home', to: '/' },
                { label: pmeStore.documentWithItems.template_name || '' },
                { label: pmeStore.documentWithItems.name || '' }
            ]"
            @apply="handleFilter"
            >
                <!-- TITLE -->
                <template #title>
                    <q-skeleton v-if="pmeStore.loading" type="text" width="260px" />
                    <span v-else>
                        {{ pmeStore.documentWithItems.template_name }}
                    </span>
                </template>

                <!-- BREADCRUMB 1 -->
                <template #breadcrumb-0>
                    <span>Home</span>
                </template>

                <!-- BREADCRUMB 2 -->
                <template #breadcrumb-1>
                    <q-skeleton v-if="pmeStore.loading" type="text" width="140px" inline />
                    <span v-else>
                        {{ pmeStore.documentWithItems.template_name }}
                    </span>
                </template>

                <!-- BREADCRUMB 3 -->
                <template #breadcrumb-2>
                    <q-skeleton v-if="pmeStore.loading" type="text" width="160px" inline />
                    <span v-else>
                        {{ pmeStore.documentWithItems.name }}
                    </span>
                </template>
            </PageComboHeader>


            <HierarchyTable v-if="pmeStore.documentWithItems.items" :items="pmeStore.documentWithItems.items || []" :document-id="pmeStore.documentWithItems.id"
                :document="pmeStore.documentWithItems" />

            <HierarchyTableSkeleton v-else-if="pmeStore.loading" />

            <InitiativeFormModal v-model="pmeStore.showInitiativeFormModal" :items="pmeStore.documentWithItems.items || []"
                :reporting-periods="pmeStore.reportingPeriods || []" @submitted="pmeStore.fetchDocument(route.params.documentId)"
                :initiative="pmeStore.selectedInitiative" />

            <InitiativeListModal
                v-model="pmeStore.showInitiativeModal"
                :indicator="pmeStore.selectedIndicator"
                :initiatives="pmeStore.initiatives"
                @edit="pmeStore.onEditInitiative"
                @accomplished="pmeStore.onMarkAsAccomplished"
                @deleted="pmeStore.removeInitiative"
                @reverted="pmeStore.revertAccomplishment"
            />

            <AccomplishmentFormModal
                v-if="pmeStore.selectedInitiative"
                v-model="pmeStore.showAccomplishmentFormModal"
                :initiative="pmeStore.selectedInitiative"
                :reporting-periods="pmeStore.reportingPeriods"
                @submitted="pmeStore.onAccomplishmentSubmitted(route.params.documentId)"
            />

        </div>
    </q-page>
</template>

<script setup>
import { watch } from 'vue'
import { useRoute } from 'vue-router'
import { usePmeStore } from 'src/stores/pme'

import PageComboHeader from 'src/components/pme/PageComboHeader.vue'
import HierarchyTable from 'src/components/pme/HierarchyTable.vue'
import HierarchyTableSkeleton from 'src/components/pme/HierarchyTableSkeleton.vue'
import InitiativeListModal from 'src/components/pme/InitiativeListModal.vue'
import InitiativeFormModal from 'src/components/pme/InitiativeFormModal.vue'
import AccomplishmentFormModal from 'src/components/pme/AccomplishmentFormModal.vue'

const route = useRoute()

const pmeStore = usePmeStore()

function handleFilter(filters) {
  pmeStore.setFilters(filters)
  pmeStore.fetchDocument(route.params.documentId)
}

watch(
    () => route.params.documentId,
    (newId) => {
        if (newId) {
            pmeStore.fetchDocument(newId)
            pmeStore.fetchReportingPeriods(newId)
        }
    },
    { immediate: true }
)
</script>
