<template>
  <q-layout view="hHh lpR fFf" class="bg-page text-primary">
    <AppHeader @toggle-drawer="toggleLeftDrawer" />

    <AppDrawer
      v-model="leftDrawerOpen"
    />

    <q-page-container class="bg-page text-primary">
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script setup>
import { ref } from 'vue'
import AppHeader from 'components/layout/AppHeader.vue'
import AppDrawer from 'components/layout/AppDrawer.vue'

const leftDrawerOpen = ref(false)

function toggleLeftDrawer () {
  leftDrawerOpen.value = !leftDrawerOpen.value
}
</script>