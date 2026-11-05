import { useRoute, useRouter } from "vue-router"
import { useAuthStore } from "@/data/auth.js"

// For actions open to any signed-in user: sends everyone else to sign in,
// and back here afterwards.
export const useRequireLogin = () => {
  const route = useRoute()
  const router = useRouter()
  const authStore = useAuthStore()
  return () => {
    if (authStore.isAuthenticated) return true
    router.push({ name: "me", query: { next: route.fullPath } })
    return false
  }
}
