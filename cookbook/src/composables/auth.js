import { createSharedComposable, useStorage } from "@vueuse/core"
import axios from "axios"
import { handleAxiosError } from "@/contrib/composables/setup.js"

export const me = useStorage("auth", {})

export const useAuth = createSharedComposable(() => {
  const whoami = () =>
    axios
      .get("/auth/whoami/")
      .then(({ data }) => (me.value = data))
      .catch(handleAxiosError("Failed to fetch auth whoami"))

  whoami()

  return { whoami }
})
