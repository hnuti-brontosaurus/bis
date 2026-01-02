import { useStorage } from "@vueuse/core"
import axios from "axios"
import { useErrorHandler } from "@/contrib/composables/errorHandler.js"

const auth = useStorage("auth", {})

let initialized = false

export function useAuth() {
  const { handleAxiosError } = useErrorHandler()
  if (!initialized)
    axios
      .get("/auth/whoami")
      .then(({ data }) => (auth.value = data))
      .catch(handleAxiosError("Failed to fetch auth whoami"))

  initialized = true
  return { auth }
}
