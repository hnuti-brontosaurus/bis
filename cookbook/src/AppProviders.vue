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
import { useAppSettings } from "@/composables/app_settings.js"

const { settings } = useAppSettings()

const magenta = "#239d46"
const lighter = "#39a759"
const darker = "#208d3f"

function scale(str, factor=1.4) {
  if (typeof str !== "string") return str;
  return str.replace(/-?\d+(?:\.\d+)?px/g, (m) => {
    const n = Number.parseFloat(m);
    const v = n * factor;
    const r = Math.floor(v);
    return `${r}px`;
  });
}
const themeOverrides = {}

const scaleEntry = (name, values) => {
  themeOverrides[name] = Object.fromEntries(Object.entries(values).map(([key, value]) => [key, scale(value)]))
}

const theme = settings.value.useDarkTheme ? darkTheme : lightTheme
Object.entries(theme).forEach(([name, entry]) => {
  if (!["common", "name"].includes(name)) {
    if (entry.self === undefined)
      return
    entry = entry.self(theme.common)
  }
  scaleEntry(name, entry)
})

themeOverrides.common.fontFamily = '"Delm", "Segoe UI", Tahoma, Geneva, Verdana, sans-serif'
themeOverrides.common.borderRadius = "10px"
themeOverrides.common.borderRadiusSmall = "10px"
themeOverrides.common.primaryColor = magenta
themeOverrides.common.primaryColorHover = settings.value.useDarkTheme ? lighter : darker
themeOverrides.common.primaryColorPressed = settings.value.useDarkTheme ? darker : lighter
themeOverrides.common.primaryColorSuppl = settings.value.useDarkTheme ? lighter : darker
themeOverrides.PageHeader.titleFontSize = scale(themeOverrides.common.fontSizeHuge, 2)
themeOverrides.PageHeader.titleTextColor = themeOverrides.common.textColorPrimary


</script>

<template>
  <n-config-provider :theme="theme" :theme-overrides="themeOverrides" abstract>
    <n-theme-editor :theme="theme">
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
