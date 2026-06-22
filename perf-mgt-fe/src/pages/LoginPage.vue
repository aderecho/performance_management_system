<template>
  <q-layout view="lHh Lpr lFf">
    <q-page-container class="bg-page text-primary q-pa-md">
      <q-page class="flex flex-center bg-page text-primary q-pa-md">
        <q-card class="q-pa-lg shadow-2 login-card" bordered>
          <q-card-section class="text-center q-pb-md">
            <div class="text-grey-9 text-h5 text-weight-bold">Sign in</div>
            <div class="text-grey-8">Sign in using your UP Cebu account</div>
          </q-card-section>

          <q-form @submit="onSubmit" class="q-gutter-md">
            <q-input
              dense
              outlined
              v-model="username"
              label="Username"
              :error="!!errors.username"
              :error-message="errors.username"
            />
            <q-input
              dense
              outlined
              v-model="password"
              type="password"
              label="Password"
              :error="!!errors.password"
              :error-message="errors.password"
            />

            <q-btn
              color="primary"
              size="md"
              label="Sign in"
              no-caps
              class="full-width"
              type="submit"
              :loading="isSubmitting"
            ></q-btn>
          </q-form>

          <div class="text-center text-grey-8 q-mt-md">
            Forgot your password?
            <a
              href="https://support.upcebu.edu.ph/open.php"
              class="text-dark text-weight-bold no-underline"
              target="_blank"
              >Request a ticket.</a
            >
          </div>

          <div class="row items-center q-gutter-md q-my-md">
            <q-separator class="col" />
            <div class="text-grey-7">or</div>
            <q-separator class="col" />
          </div>

          <q-btn outline class="full-width" no-caps @click="onClickSso()">
            <q-img
              class="q-mr-sm"
              alt="Google logo"
              src="~assets/google/16.svg"
              width="16px"
              height="16px"
            />
            <div>Sign in using UP Mail</div>
          </q-btn>
        </q-card>
      </q-page>
    </q-page-container>
  </q-layout>
</template>
<script setup>
import { useForm, useField } from 'vee-validate'
import { toTypedSchema } from '@vee-validate/zod'
import { useRouter } from 'vue-router'
import { loginSchema } from 'src/validators/auth.schema'
import { useAuthStore } from 'src/stores/auth'
import { notify } from 'src/utils/notify'

const authStore = useAuthStore()
const router = useRouter()

const { handleSubmit, errors, resetForm, isSubmitting } = useForm({
  validationSchema: toTypedSchema(loginSchema),
  initialValues: {
    username: '',
    password: '',
  },
})

const { value: username } = useField('username')
const { value: password } = useField('password')

const onSubmit = handleSubmit(async (values) => {
  try {
    await authStore.login(values.username, values.password)
    notify.positive(`Welcome back, ${values.username}!`)
    resetForm()
    router.push('/dashboard')
  } catch {
    notify.negative('Unable to sign in. Please check your credentials and try again.')
  }
})

const onClickSso = () => {
  notify.warning('SSO feature is under development!')
}
</script>
