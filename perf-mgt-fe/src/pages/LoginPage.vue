<template>
    <q-layout view="lHh Lpr lFf">
        <q-page-container class="bg-page text-primary q-pa-md">
            <q-page class="flex flex-center bg-page text-primary q-pa-md">
                <q-card class="q-pa-md shadow-2 my_card" bordered>
                    <q-card-section class="text-center">
                        <div class="text-grey-9 text-h5 text-weight-bold">Sign in</div>
                        <div class="text-grey-8">Sign in using your UP Cebu account</div>
                    </q-card-section>
                    <q-form @submit="onSubmit" class="q-gutter-sm">
                        <q-card-section>
                            <q-input
                                dense
                                outlined
                                v-model="username"
                                label="Username"
                                :error="!!errors.username"
                                :error-message="errors.username"
                            />
                            <q-input
                                class="q-mb-xs"
                                dense
                                outlined
                                v-model="password"
                                type="password"
                                label="Password"
                                :error="!!errors.password"
                                :error-message="errors.password"
                            />

                            <q-btn color="primary" size="md" label="Sign in" no-caps class="full-width q-pt-xs"
                                type="submit" :loading="isSubmitting"></q-btn>
                        </q-card-section>
                    </q-form>
                    <q-card-section class="text-center q-pt-none">
                        <div class="text-grey-8">Forgot your password?
                            <a href="https://support.upcebu.edu.ph/open.php" class="text-dark text-weight-bold"
                                style="text-decoration: none" target="_blank">Request a ticket.</a>
                        </div>
                    </q-card-section>

                    <div class="row items-center q-gutter-md">
                        <q-separator class="col" />
                        <div>or</div>
                        <q-separator class="col" />
                    </div>

                    <q-card-section class="text-center q-pt-none q-mt-md">
                        <q-btn outline class="full-width" @click="onClickSso()" >
                            <q-img class="q-mr-sm" alt="Quasar logo" src="~assets/google/16.svg"
                                style="width: 16px; height: 16px" />
                            <div>Sign in using UP Mail</div>
                        </q-btn>

                    </q-card-section>

                </q-card>
            </q-page>
        </q-page-container>
    </q-layout>
</template>
<script setup>
import { useForm, useField } from 'vee-validate'
import { toFormValidator } from '@vee-validate/zod'
import { loginSchema } from 'src/validators/auth.schema'
import { useAuthStore } from 'src/stores/auth';
import { notify } from 'src/utils/notify'

const authStore = useAuthStore();

const { handleSubmit, errors, resetForm, isSubmitting } = useForm({
  validationSchema: toFormValidator(loginSchema),
  initialValues: {
    username: '',
    password: '',
  },
})

const { value: username } = useField('username')
const { value: password } = useField('password')

const onSubmit = handleSubmit(async (values) => {
  await authStore.login(values.username, values.password)
  resetForm()
})

const onClickSso = () => {
    notify.warning('SSO feature is under development!')
}

</script>
<style scoped>
.my_card {
    width: 25rem;
    border-radius: 8px;
    box-shadow: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
}
</style>