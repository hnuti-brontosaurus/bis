<script setup>
import { NFlex, NH1, NText } from "naive-ui"
import { theme } from "@/composables/theme.js"
import ProfileSettings from "@/components/auth/ProfileSettings.vue"
import { me } from "@/composables/auth.js"
import LoginForm from "@/components/auth/LoginForm.vue"
</script>

<template>
  <ProfileSettings v-if="me.is_authenticated" />
  <LoginForm v-else />
</template>

<style scoped></style>
