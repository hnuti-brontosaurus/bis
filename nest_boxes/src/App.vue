<script setup>
import { RouterView, useRoute } from "vue-router"
import { csCZ, dateCsCZ, NConfigProvider, NMessageProvider } from "naive-ui"

import AppHeader from "@/components/app/AppHeader.vue"
import { baseTheme, theme } from "@/composables/theme.js"

const route = useRoute()
</script>

<template>
  <n-config-provider
    :theme="baseTheme"
    :theme-overrides="theme"
    :locale="csCZ"
    :date-locale="dateCsCZ"
    abstract
  >
    <n-message-provider>
      <div class="screen" :class="{ 'full-height': route.meta.map }">
        <AppHeader v-if="!route.meta.volunteer" />
        <RouterView />
      </div>
    </n-message-provider>
  </n-config-provider>
</template>

<style scoped>
.screen {
  display: flex;
  flex-direction: column;
  min-height: 100dvh;
}

.full-height {
  height: 100dvh;
}
</style>
