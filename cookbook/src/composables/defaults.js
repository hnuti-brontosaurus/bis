import { useLocalStorage } from "@vueuse/core"
import axios from "axios"
import { useErrorHandler } from "@/contrib/composables/errorHandler.js"

const defaults = useLocalStorage(
  "defaults",
  {
    audiences: {},
    applications: {},
    transaction_types: [],
    contact_policies: [],
    product_types: [],
    action_ore_options: [],
    action_categories: [],
    action_types: [],
    tls_campaigns: [],
    tls_partners: [],
  },
  { mergeDefaults: true },
)

let initialized = false

export function useDefaults() {
  const { handleAxiosError } = useErrorHandler()
  if (!initialized)
    axios
      .get("/defaults")
      .then(({ data }) => Object.assign(defaults.value, data))
      .catch(handleAxiosError("Failed to fetch defaults"))

  initialized = true

  return { defaults }
}
