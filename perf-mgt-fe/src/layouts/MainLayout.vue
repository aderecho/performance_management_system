<template>
  <q-layout view="lHh lpR fFf" class="bg-page text-primary main-layout">
    <AppHeader :drawer-open="leftDrawerOpen" @toggle-drawer="toggleLeftDrawer" />

    <AppDrawer
      v-model="leftDrawerOpen"
    />

    <q-page-container class="bg-page text-primary main-router-view">
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script setup>
import { ref } from 'vue'
import { useQuasar } from 'quasar'
import AppHeader from 'components/layout/AppHeader.vue'
import AppDrawer from 'components/layout/AppDrawer.vue'

const $q = useQuasar()

// Open by default on desktop (matches the drawer's show-if-above breakpoint),
// hidden on smaller screens.
const leftDrawerOpen = ref($q.screen.gt.sm)

function toggleLeftDrawer () {
  leftDrawerOpen.value = !leftDrawerOpen.value
}
</script>
