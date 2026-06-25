<template>
  <q-btn
    v-if="authStore.user"
    flat
    no-caps
    dense
    class="account-trigger"
    :aria-label="`Account menu for ${fullName}`"
  >
    <div class="row items-center no-wrap">
      <InitialsAvatar
        :first-name="authStore.user.first_name"
        :last-name="authStore.user.last_name"
        size="32px"
      />

      <div v-if="$q.screen.gt.sm" class="column items-start q-ml-sm">
        <span class="account-trigger__name ellipsis">{{ fullName }}</span>
        <span class="account-trigger__role ellipsis">{{ roleLabel }}</span>
      </div>

      <q-icon v-if="$q.screen.gt.sm" name="expand_more" size="18px" class="q-ml-xs text-white" />
    </div>

    <q-menu anchor="bottom right" self="top right" :offset="[0, 10]">
      <q-card flat class="account-menu">
        <!-- Identity -->
        <div class="account-menu__header row items-center no-wrap q-gutter-sm">
          <InitialsAvatar
            :first-name="authStore.user.first_name"
            :last-name="authStore.user.last_name"
            size="44px"
          />
          <div class="col min-w-0">
            <div class="account-menu__name ellipsis">{{ fullName }}</div>
            <div class="account-menu__email ellipsis">{{ authStore.user.email }}</div>
            <q-chip
              dense
              square
              color="primary"
              text-color="white"
              class="account-menu__role-chip q-mt-xs"
            >
              <component :is="roleIcon" :size="13" :stroke-width="2.5" class="q-mr-xs" />
              {{ roleLabel }}
            </q-chip>
          </div>
        </div>

        <q-separator />

        <!-- Preferences -->
        <q-list padding>
          <q-item class="account-menu__item" @click="themeStore.setDarkMode(!themeStore.darkMode)">
            <q-item-section avatar>
              <q-icon :name="themeStore.darkMode ? 'dark_mode' : 'light_mode'" color="primary" />
            </q-item-section>
            <q-item-section>Dark Mode</q-item-section>
            <q-item-section side>
              <q-toggle
                :model-value="themeStore.darkMode"
                color="primary"
                aria-label="Toggle dark mode"
                @update:model-value="themeStore.setDarkMode"
                @click.stop
              />
            </q-item-section>
          </q-item>
        </q-list>

        <q-separator />

        <!-- Actions -->
        <div class="q-pa-sm">
          <q-btn
            class="full-width"
            color="primary"
            unelevated
            no-caps
            icon="logout"
            label="Logout"
            v-close-popup
            @click="handleLogout"
          />
        </div>
      </q-card>
    </q-menu>
  </q-btn>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from 'src/stores/auth'
import { useThemeStore } from 'src/stores/theme'
import InitialsAvatar from './InitialsAvatar.vue'
import { notify } from 'src/utils/notify'
import { BadgeCheck, ShieldCheck } from 'lucide-vue-next'

const authStore = useAuthStore()
const themeStore = useThemeStore()
const router = useRouter()

const fullName = computed(() => {
  const user = authStore.user || {}
  const name = [user.first_name, user.last_name].filter(Boolean).join(' ').trim()
  return name || user.email || 'User'
})

const roleLabel = computed(() => {
  if (!authStore.user) return ''
  if (authStore.isSuperAdmin) return 'Super Admin'
  const roles = authStore.roles || []
  return roles.length ? roles.join(', ') : 'Member'
})

const roleIcon = computed(() => (authStore.isSuperAdmin ? ShieldCheck : BadgeCheck))

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
