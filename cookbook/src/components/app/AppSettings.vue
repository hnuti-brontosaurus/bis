<script setup>
import { NButton, NDropdown, useMessage } from "naive-ui"
import { useRender } from "@/contrib/composables/render.js"
import { faGear } from "@fortawesome/free-solid-svg-icons"

const { icon } = useRender()
const message = useMessage()

const options = [
  {
    key: "theme",
    label: `Switch to ${settings.value.useDarkTheme ? "light" : "dark"} theme`,
  },
  {
    key: "refresh",
    label: `Remove local settings`,
  },
  {
    key: "logout",
    label: "Logout",
  },
]

function onSelect(value) {
  if (value === "theme") {
    settings.value.useDarkTheme = !settings.value.useDarkTheme
    location.reload()
  }

  if (value === "logout") {
    message.error("Not implemented")
  }

  if (value === "refresh") {
    localStorage.clear()
    location.reload()
  }
}
</script>

<template>
  <n-dropdown :on-select="onSelect" :options="options" trigger="click">
    <n-button :render-icon="icon(faGear)" type="primary"></n-button>
  </n-dropdown>
</template>

<style scoped></style>
