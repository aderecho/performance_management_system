<template>
  <q-btn round flat padding="none">
    <initialsAvatar :first-name="authStore.user.first_name" :last-name="authStore.user.last_name"></initialsAvatar> 

    <q-menu anchor="bottom right" self="top right">
      <q-card class="bg-card text-primary" style="min-width:280px">
        <q-card-section class="row no-wrap q-pa-md">

          <div class="column">
            <div class="text-h6 q-mb-md">Settings</div>
            <q-toggle
              :model-value="configStore.darkMode"
              label="Dark Mode"
              checked-icon="dark_mode"
              unchecked-icon="light_mode"
              @update:model-value="configStore.setDarkMode"
            />
          </div>

          <q-separator vertical inset class="q-mx-lg" />

          <div class="column items-center">
            <initialsAvatar :first-name="authStore.user.first_name" :last-name="authStore.user.last_name"></initialsAvatar> 

            <div class="text-subtitle1 q-mt-md q-mb-xs">
              {{ authStore.user.username }}
            </div>

            <q-btn
              color="primary"
              label="Logout"
              size="sm"
              class="q-mt-sm"
              v-close-popup
              @click="authStore.logout"
            />
          </div>

        </q-card-section>
      </q-card>
    </q-menu>
  </q-btn>
</template>

<script setup>
import { useAuthStore } from 'src/stores/auth'
import { useConfigStore } from 'src/stores/config'
import InitialsAvatar from './InitialsAvatar.vue';

const authStore = useAuthStore()
const configStore = useConfigStore()
</script>