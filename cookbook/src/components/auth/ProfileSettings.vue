<script setup>
import {
  NButton,
  NButtonGroup,
  NDropdown,
  NFlex,
  NForm,
  NGrid,
  NGridItem,
  NImage,
  useMessage,
  useThemeVars,
} from "naive-ui"
import { useRender } from "@/contrib/composables/render.js"
import { faUser } from "@fortawesome/free-regular-svg-icons"
import { faBars } from "@fortawesome/free-solid-svg-icons"
import { useRouter } from "vue-router"
import { theme } from "@/composables/theme.js"
import { _, translatedKey } from "@/composables/translations.js"
import { me, useAuth } from "@/composables/auth.js"
import { computed, ref } from "vue"
import { useDarkTheme } from "@/composables/settings.js"
import AppPage from "@/components/app/AppPage.vue"
import GenericForm from "@/contrib/components/GenericForm.vue"
import VueHcaptcha from "@hcaptcha/vue3-hcaptcha"
import { useConnector } from "@/composables/connector.js"
import { handleAxiosError } from "@/contrib/composables/setup.js"
const router = useRouter()
const form = ref()
const auth = useAuth()
const chefs = useConnector("chefs", 0)
const loading = ref(false)
const message = useMessage()
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
])
const save = async () => {
  loading.value = true
  try {
    await form.value.validate()
    await chefs.upsert(me.value.chef)
    await auth.whoami()
    message.info("Uloženo")
    await router.back()
  } catch (e) {
    handleAxiosError(_.value.profile.error_saving)(e)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <AppPage :title="me.is_chef ? _.profile.title : _.profile.new">
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
