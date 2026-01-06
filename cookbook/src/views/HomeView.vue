<script setup>
import { NFlex, NH1, NText } from "naive-ui"
import { theme } from "@/composables/theme.js"
</script>

<template>
  <n-flex vertical align="center">
    <n-h1 style="text-align: center; margin-bottom: 0">
      <n-text type="primary">Veganská Brontosauří kuchařka</n-text>
    </n-h1>
    <n-text
      type="primary"
      :style="{ 'margin-bottom': theme.Typography.headerMargin1.split(' ')[2] }"
      >*nejen pro Brontosaury</n-text
    >
  </n-flex>
</template>

<style scoped></style>
