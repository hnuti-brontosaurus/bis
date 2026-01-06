<script setup>
import { useSetup } from "@/contrib/composables/setup.js"
import AppLayout from "@/AppLayout.vue"
import { useTranslations } from "@/composables/translations.js"
import { useAuth } from "@/composables/auth.js"

useSetup()
useTranslations()
useAuth()
</script>

<template>
  <AppLayout />
</template>

<style scoped></style>
