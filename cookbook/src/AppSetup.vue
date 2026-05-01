<script setup>
import { useSetup } from "@/contrib/composables/setup.js"
import AppLayout from "@/AppLayout.vue"
import { useTranslations } from "@/composables/translations.js"
import { useAuthStore } from "@/data/auth.js"

useSetup()
useTranslations()
useAuthStore().whoami()
</script>

<template>
  <AppLayout />
</template>

<style scoped></style>
