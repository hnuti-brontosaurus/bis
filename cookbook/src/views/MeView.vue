<script setup>
import { NAlert } from "naive-ui"
import { computed } from "vue"
import { useRoute } from "vue-router"
import ProfileSettings from "@/components/auth/ProfileSettings.vue"
import { useAuthStore } from "@/data/auth.js"
import LoginForm from "@/components/auth/LoginForm.vue"
import { storeToRefs } from "pinia"
import { _ } from "@/composables/translations.js"

const route = useRoute()
const { isAuthenticated, isChef } = storeToRefs(useAuthStore())

// Shown whenever the user landed here from a chef-only route
// (the router's `requiresAuth` guard sets `next`).
const wasRedirected = computed(() => !!route.query.next)
const banner = computed(() => {
  if (!wasRedirected.value) return null
  if (!isAuthenticated.value) return _.value.profile.chef_required_login
  if (!isChef.value) return _.value.profile.chef_required_profile
  return null
})
</script>

<template>
  <div>
    <n-alert
      v-if="banner"
      :title="banner"
      type="info"
      style="margin: 1rem 1rem 0"
      :show-icon="true"
    />
    <ProfileSettings v-if="isAuthenticated" />
    <LoginForm v-else />
  </div>
</template>

<style scoped></style>
