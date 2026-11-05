import { defineStore } from "pinia"
import { computed, ref } from "vue"

import { APP_PATH } from "@/config.js"
import { client } from "@/data/client.js"
import { reportError } from "@/data/errors.js"

// The BIS login keeps its own token in localStorage; a stale one makes
// `/login` bounce straight back here without a session. Going through
// `/logout` first clears it, the same way Django's LOGIN_URL does.
export const loginUrl = path =>
  `/logout?next=${encodeURIComponent(`/login?next=${encodeURIComponent(APP_PATH + path)}`)}`

export const logoutUrl = path => `/logout?next=${encodeURIComponent(APP_PATH + path)}`

export const useAuthStore = defineStore("auth", () => {
  // Stays null when whoami fails: unknown, which is not the same as anonymous.
  const me = ref(null)

  // Again after a batch is created or closed, for the header's badge
  const refresh = () =>
    client
      .get("/whoami/")
      .then(({ data }) => {
        me.value = data
      })
      .catch(reportError)

  const loaded = refresh()

  const isAuthenticated = computed(() => Boolean(me.value?.is_authenticated))
  const isManager = computed(() => Boolean(me.value?.is_manager))
  const openBatchCount = computed(() => me.value?.open_batch_count ?? 0)
  const initials = computed(() => {
    const user = me.value?.user
    return user ? `${user.first_name.charAt(0)}${user.last_name.charAt(0)}` : ""
  })

  const isAnonymous = computed(() => me.value?.is_authenticated === false)

  return {
    me,
    loaded,
    refresh,
    isAuthenticated,
    isAnonymous,
    isManager,
    openBatchCount,
    initials,
  }
})
