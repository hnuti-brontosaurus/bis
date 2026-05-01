import { defineStore } from "pinia"
import { computed, ref } from "vue"
import { client } from "./client.js"
import { handleAxiosError } from "@/contrib/composables/setup.js"

export const authApi = {
  whoami: () => client.get("/auth/whoami/").then(r => r.data),
  checkEmail: (email, config) =>
    client.post("/auth/check_email/", { email }, config).then(r => r.data),
  validatePassword: password =>
    client.post("/auth/validate_password/", { password }).then(r => r.data),
  login: payload => client.post("/auth/login/", payload).then(r => r.data),
  register: payload => client.post("/auth/register/", payload).then(r => r.data),
}

/**
 * Default shape of the auth state. Mirrors the response of GET /auth/whoami/
 * (see backend `api/cookbook/views/auth.py#get_user_data`). Anonymous users
 * get this exact object; authenticated users additionally have `user.token`
 * and (for chefs) the full ChefSerializer payload under `chef`.
 *
 * @typedef {Object} AuthState
 * @property {boolean} is_authenticated
 * @property {boolean} is_chef
 * @property {boolean} is_editor
 * @property {{ first_name?: string, last_name?: string, email?: string, token?: string }} user
 * @property {{ user_id?: number, name?: string, email?: string, photo?: object, is_editor?: boolean }} chef
 */
export const AUTH_SHAPE = Object.freeze({
  is_authenticated: false,
  is_chef: false,
  is_editor: false,
  user: {},
  chef: {},
})

const blankAuth = () => ({ ...AUTH_SHAPE, user: {}, chef: {} })

export const useAuthStore = defineStore(
  "auth",
  () => {
    const me = ref(blankAuth())

    const token = computed(() => me.value.user?.token ?? null)
    const isAuthenticated = computed(() => !!me.value.is_authenticated)
    const isChef = computed(() => !!me.value.is_chef)

    const setMe = data => {
      me.value = { ...blankAuth(), ...data }
    }

    const whoami = async () => {
      try {
        setMe(await authApi.whoami())
      } catch (e) {
        handleAxiosError("Failed to fetch auth whoami")(e)
      }
    }

    const logout = () => {
      me.value = blankAuth()
    }

    return { me, token, isAuthenticated, isChef, setMe, whoami, logout }
  },
  // Versioned key so a shape change here (or the move from the old
  // useStorage("auth", ...) ref) doesn't try to hydrate stale data.
  { persist: { key: "cookbook:auth:v1" } },
)

/**
 * Token getter for non-component code (e.g. axios interceptors). Returns
 * the token string, or null when no user is logged in. Pinia auto-unwraps
 * the underlying computed on store access, so this is a plain value.
 */
export const getAuthToken = () => useAuthStore().token
