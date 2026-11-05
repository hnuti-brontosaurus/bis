<script setup>
import { NAlert } from "naive-ui"
import { computed } from "vue"
import { useRoute, useRouter } from "vue-router"
import ProfileSettings from "@/components/auth/ProfileSettings.vue"
import { useAuthStore } from "@/data/auth.js"
import LoginForm from "@/components/auth/LoginForm.vue"
import { storeToRefs } from "pinia"
import { _ } from "@/composables/translations.js"

const route = useRoute()
const router = useRouter()
const { isAuthenticated, isChef } = storeToRefs(useAuthStore())

// Shown whenever the user landed here from a page that needs them signed in:
// a chef-only route (the router's `requiresAuth` guard sets `next`) or an
// action open to any signed-in user.
const needsChef = computed(
  () => !!route.query.next && !!router.resolve(route.query.next).meta.requiresAuth,
)
const banner = computed(() => {
  if (!route.query.next) return null
  if (!isAuthenticated.value)
    return needsChef.value
      ? _.value.profile.chef_required_login
      : _.value.profile.login_required
  if (!isChef.value && needsChef.value) return _.value.profile.chef_required_profile
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
