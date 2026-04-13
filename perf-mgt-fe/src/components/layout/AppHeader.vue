<template>
  <q-header elevated class="bg-surface text-primary" height-hint="64">
    <q-toolbar class="GNL__toolbar">

      <q-btn
        flat dense round
        icon="menu"
        color="white"
        class="q-mr-sm"
        @click="$emit('toggle-drawer')"
      />

      <q-toolbar-title
        v-if="$q.screen.gt.xs"
        shrink
        class="row items-center no-wrap text-white text-weight-bold q-ml-sm"
      >
        UPlan360
      </q-toolbar-title>

      <q-space />

      <div class="row items-center no-wrap q-gutter-sm">
        <AppLauncher />
        <!-- <AppLauncher v-if="$q.screen.gt.sm" /> -->
        <UserAvatarMenu />
      </div>

    </q-toolbar>
  </q-header>
</template>

<script setup>
import AppLauncher from './AppLauncher.vue'
import UserAvatarMenu from '../UserAvatarMenu.vue';

defineEmits(['toggle-drawer'])
</script>