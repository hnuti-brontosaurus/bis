<script setup>
import { useSetup } from "@/contrib/composables/setup.js"
import AppLayout from "@/AppLayout.vue"

const setup = useSetup()
setup.setupAxios()
setup.setupErrorHandler()
</script>

<template>
  <AppLayout />
</template>

<style scoped></style>
