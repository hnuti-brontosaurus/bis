<script setup>
import { useSetup } from "@/contrib/composables/setup.js"
import AppLayout from "@/AppLayout.vue"
import CartConflictModal from "@/components/cart/CartConflictModal.vue"
import { useTranslations } from "@/composables/translations.js"
import { useAuthStore } from "@/data/auth.js"
import { useCartStore } from "@/data/cart.js"

useSetup()
useTranslations()
useAuthStore().whoami()
useCartStore()
</script>

<template>
  <AppLayout />
  <CartConflictModal />
</template>

<style scoped></style>
