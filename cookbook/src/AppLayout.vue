<script setup>
import { RouterView } from "vue-router"
import { NLayout, NLayoutFooter, NLayoutHeader, NFlex } from "naive-ui"
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
      <main
        class="page-content"
        :style="{ minHeight: `calc(100vh - ${theme.common.heightHuge})` }"
      >
        <RouterView />
      </main>
      <n-layout-footer bordered class="muted small" style="padding: 1rem">
        <n-flex justify="center"> brontosaurus.cz </n-flex>
      </n-layout-footer>
    </n-layout>
  </n-layout>
</template>
