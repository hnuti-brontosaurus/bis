<script setup>
import { useRoute, useRouter } from "vue-router"
import { _ } from "@/composables/translations.js"
import { me } from "@/composables/auth.js"
import { computed, ref, watch } from "vue"
import { NForm } from "naive-ui"
import { watchDebounced } from "@vueuse/core"
import { authApi } from "@/data/auth.js"
import { handleAxiosError } from "@/contrib/composables/setup.js"
import AppPage from "@/components/app/AppPage.vue"
import { useDarkTheme } from "@/composables/settings.js"
import VueHcaptcha from "@hcaptcha/vue3-hcaptcha"
import GenericForm from "@/contrib/components/GenericForm.vue"

const user = ref({})
const emailProps = ref({})
const emailExists = ref()
const hcaptcha = ref()
const form = ref()
const registerLoading = ref(false)
const router = useRouter()
const route = useRoute()
let controller

watch(
  () => user.value.email,
  () => {
    emailProps.value.loading = false
    emailProps.value.validationStatus = undefined
    emailProps.value.feedback = ""
    emailExists.value = undefined
  },
)

watchDebounced(
  () => user.value.email,
  async () => {
    if (!user.value.email) return
    emailProps.value.loading = true
    controller?.abort()
    controller = new AbortController()
    try {
      emailExists.value = await authApi.checkEmail(user.value.email, {
        signal: controller.signal,
      })
    } catch (e) {
      if (e.status === 400) {
        emailProps.value.feedback = _.value.login.bad_email
        emailProps.value.validationStatus = "error"
      } else {
        handleAxiosError("Error checking login email")(e)
      }
    } finally {
      emailProps.value.loading = false
    }
  },
  { debounce: 1000, immediate: true },
)

const register = async () => {
  registerLoading.value = true
  try {
    await form.value.validate()
    const { response } = await hcaptcha.value.executeAsync()
    me.value = await authApi.register({ ...user.value, response })
  } catch (e) {
    handleAxiosError(_.value.login.registration_error)(e)
  } finally {
    registerLoading.value = false
  }
}

const login = async () => {
  registerLoading.value = true
  try {
    await form.value.validate()
    me.value = await authApi.login({ ...user.value })
    if (me.value.is_chef && route.query.next) router.push(route.query.next)
  } catch (e) {
    handleAxiosError(_.value.login.login_error)(e)
  } finally {
    registerLoading.value = false
  }
}

const inputs = computed(() => {
  const data = [
    {
      type: "text",
      key: "email",
      required: true,
      item: emailProps.value,
    },
  ]

  if (emailExists.value === false)
    data.push(
      ...[
        {
          type: "title",
          title: _.value.login.unknown_email,
          new_line: true,
          hide_feedback: true,
        },
        { type: "text", key: "first_name", required: true, new_line: true },
        { type: "text", key: "last_name", required: true },
        {
          type: "text",
          key: "password",
          required: true,
          extra: { type: "password" },
          rules: [
            {
              trigger: "change",
              validator: async (_, value) => {
                try {
                  await authApi.validatePassword(value)
                  return true
                } catch (e) {
                  throw new Error(e.response.data.join(" "), { cause: e })
                }
              },
            },
          ],
        },
        {
          type: "text",
          key: "password2",
          required: true,
          extra: { type: "password" },
          rules: [
            {
              message: _.value.login.passwords_not_same,
              trigger: "change",
              validator: (_, value) => user.value.password === value,
            },
          ],
        },
        {
          span: 2,
          action: {
            label: _.value.login.register,
            onClick: register,
            extra: { loading: registerLoading.value, disabled: registerLoading.value },
          },
        },
      ],
    )

  if (emailExists.value === true)
    data.push(
      ...[
        { type: "text", key: "password", required: true, extra: { type: "password" } },
        {
          span: 2,
          action: {
            label: _.value.login.login,
            onClick: login,
            extra: { loading: registerLoading.value, disabled: registerLoading.value },
          },
        },
      ],
    )

  return data
})

const submit = () =>
  emailExists.value === true ? login() : emailExists.value === false ? register() : null
</script>

<template>
  <AppPage :title="_.login.title">
    <n-form ref="form" :model="user" @keydown.enter="submit">
      <GenericForm v-model:data="user" :inputs="inputs" group="login" />
      <vue-hcaptcha
        ref="hcaptcha"
        sitekey="12a8ba44-b54e-4346-b426-585e191acf7c"
        size="invisible"
        :reCaptchaCompat="false"
        :theme="useDarkTheme ? 'dark' : 'light'"
      ></vue-hcaptcha>
    </n-form>
  </AppPage>
</template>

<style scoped></style>
