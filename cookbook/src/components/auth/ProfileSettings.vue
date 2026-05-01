<script setup>
import { NForm, useMessage } from "naive-ui"
import { useRouter } from "vue-router"
import { _ } from "@/composables/translations.js"
import { useAuthStore } from "@/data/auth.js"
import { computed, ref } from "vue"
import { settings, useDarkTheme } from "@/composables/settings.js"
import AppPage from "@/components/app/AppPage.vue"
import GenericForm from "@/contrib/components/GenericForm.vue"
import VueHcaptcha from "@hcaptcha/vue3-hcaptcha"
import { useChefsStore } from "@/data/chefs.js"
import { handleAxiosError } from "@/contrib/composables/setup.js"
import { storeToRefs } from "pinia"

const router = useRouter()
const form = ref()
const authStore = useAuthStore()
const { me, isChef } = storeToRefs(authStore)
const chefsStore = useChefsStore()
const loading = ref(false)
const message = useMessage()
const darkThemeChecked = computed({
  get: () => useDarkTheme.value,
  set: value => {
    settings.value.darkTheme = value
  },
})
const inputs = computed(() => [
  { type: "text", key: "name", required: true },
  { type: "text", key: "email", required: true },
  {
    type: "image",
    key: "photo",
    required: true,
    span: 2,
    action: {
      label: _.value.profile.save,
      onClick: save,
      extra: { loading: loading.value, disabled: loading.value },
    },
  },
  {
    type: "checkboxes",
    new_line: true,
    span: 2,
    checkboxes: [
      {
        key: "darkTheme",
        label: _.value.profile.dark_theme,
        value: darkThemeChecked,
      },
    ],
  },
])
const save = async () => {
  loading.value = true
  try {
    await form.value.validate()
    await chefsStore.save(me.value.chef)
    await authStore.whoami()
    message.info(_.value.profile.saved)
    router.back()
  } catch (e) {
    handleAxiosError(_.value.profile.error_saving)(e)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <AppPage :title="isChef ? _.profile.title : _.profile.new">
    <n-form ref="form" :model="me.chef" @keydown.enter="save">
      <GenericForm v-model:data="me.chef" :inputs="inputs" group="Chef" />
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
