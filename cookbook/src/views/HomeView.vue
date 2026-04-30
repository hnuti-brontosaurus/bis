<script setup>
import { NFlex, NH1, NText } from "naive-ui"
import { theme } from "@/composables/theme.js"
import { _ } from "@/composables/translations.js"
</script>

<template>
  <n-flex vertical align="center">
    <n-h1 style="text-align: center; margin-bottom: 0">
      <n-text type="primary">{{ _.home.title }}</n-text>
    </n-h1>
    <n-text
      type="primary"
      :style="{ 'margin-bottom': theme.Typography.headerMargin1.split(' ')[2] }"
      >{{ _.home.subtitle }}</n-text
    >
  </n-flex>
</template>

<style scoped></style>
