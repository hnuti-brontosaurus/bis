<script setup>
import { RouterView } from "vue-router"
import {
  NLayout,
  NLayoutContent,
  NLayoutFooter,
  NLayoutHeader,
  NFlex,
  useThemeVars,
} from "naive-ui"
import AppHeader from "@/components/app/AppHeader.vue"
import { theme } from "@/composables/theme.js"
</script>

<template>
  <n-layout position="absolute" style="height: 100%">
    <n-layout-header bordered :style="{ height: theme.common.heightHuge }">
      <AppHeader />
    </n-layout-header>
    <n-layout
      position="absolute"
      :style="{ top: theme.common.heightHuge }"
      :native-scrollbar="false"
    >
      <n-layout-content
        :content-style="`padding: 2rem; margin: 0 auto; max-width: 1024px; min-height: calc(100vh - ${theme.common.heightHuge})`"
      >
        <RouterView />
      </n-layout-content>
      <n-layout-footer bordered style="padding: 1rem">
        <n-flex justify="center"> brontosaurus.cz </n-flex>
      </n-layout-footer>
    </n-layout>
  </n-layout>
</template>

<style scoped></style>
