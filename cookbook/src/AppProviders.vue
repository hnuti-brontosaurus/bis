<script setup>
import {
  darkTheme,
  lightTheme,
  NConfigProvider,
  NDialogProvider,
  NMessageProvider,
  NModalProvider,
  NNotificationProvider,
  NThemeEditor,
  NGlobalStyle,
} from "naive-ui"
import AppSetup from "@/AppSetup.vue"
import { baseTheme, theme } from "@/composables/theme.js"

const breakpoints = { xs: 600, s: 640, m: 800, l: 1280, xl: 1536, xxl: 1920 }
</script>

<template>
  <n-config-provider
    :theme="baseTheme"
    :theme-overrides="theme"
    abstract
    :breakpoints="breakpoints"
  >
    <n-theme-editor :theme="baseTheme">
      <n-global-style />
      <n-message-provider>
        <n-notification-provider>
          <n-modal-provider>
            <n-dialog-provider>
              <AppSetup></AppSetup>
            </n-dialog-provider>
          </n-modal-provider>
        </n-notification-provider>
      </n-message-provider>
    </n-theme-editor>
  </n-config-provider>
</template>

<style scoped></style>
