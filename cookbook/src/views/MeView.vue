<script setup>
import ProfileSettings from "@/components/auth/ProfileSettings.vue"
import { useAuthStore } from "@/data/auth.js"
import LoginForm from "@/components/auth/LoginForm.vue"
import { storeToRefs } from "pinia"

const { isAuthenticated } = storeToRefs(useAuthStore())
</script>

<template>
  <ProfileSettings v-if="isAuthenticated" />
  <LoginForm v-else />
</template>

<style scoped></style>
