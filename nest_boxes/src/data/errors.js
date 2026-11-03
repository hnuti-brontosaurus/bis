import { computed } from "vue"
import { createDiscreteApi } from "naive-ui"

import { baseTheme, theme } from "@/composables/theme.js"

const { message } = createDiscreteApi(["message"], {
  configProviderProps: computed(() => ({
    theme: baseTheme.value,
    themeOverrides: theme.value,
  })),
})

export const reportError = error => {
  message.error(
    error.response
      ? `Server odpověděl chybou ${error.response.status}.`
      : "Server se nepodařilo zastihnout.",
  )
  console.error(error)
}
