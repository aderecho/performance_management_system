<template>
  <q-btn v-if="authStore.user" round flat padding="none">
    <initialsAvatar :first-name="authStore.user.first_name" :last-name="authStore.user.last_name"></initialsAvatar>

    <q-menu anchor="bottom right" self="top right">
      <q-card class="bg-card text-primary menu-card">
        <q-card-section class="row no-wrap q-pa-md">
          <div class="column">
            <div class="text-h6 q-mb-md">Settings</div>
            <q-toggle :model-value="themeStore.darkMode" label="Dark Mode" checked-icon="dark_mode"
              unchecked-icon="light_mode" @update:model-value="themeStore.setDarkMode" />
          </div>

          <q-separator vertical inset class="q-mx-lg" />

          <div class="column items-center">
            <initialsAvatar :first-name="authStore.user.first_name" :last-name="authStore.user.last_name">
            </initialsAvatar>

            <div class="text-subtitle1 q-mt-md q-mb-xs">
              {{ authStore.user.username }}
            </div>

            <q-btn color="primary" label="Logout" size="sm" class="q-mt-sm" v-close-popup @click="handleLogout" />
          </div>
        </q-card-section>
      </q-card>
    </q-menu>
  </q-btn>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from 'src/stores/auth'
import { useThemeStore } from 'src/stores/theme'
import InitialsAvatar from './InitialsAvatar.vue'
import { notify } from 'src/utils/notify'

const authStore = useAuthStore()
const themeStore = useThemeStore()
const router = useRouter()

async function handleLogout() {
  try {
    await authStore.logout()
  } catch {
    notify.warning('Local session ended, but server logout failed.')
  } finally {
    router.push('/login')
  }
}
</script>
