import { computed } from "vue"
import { createDiscreteApi } from "naive-ui"

import { baseTheme, theme } from "@/composables/theme.js"

const { message } = createDiscreteApi(["message"], {
  configProviderProps: computed(() => ({
    theme: baseTheme.value,
    themeOverrides: theme.value,
  })),
})

// A 400 says what is wrong as {field: [messages]}, or a list, or a string.
const firstMessage = body =>
  typeof body === "string"
    ? body
    : Array.isArray(body)
      ? firstMessage(body[0])
      : body && typeof body === "object"
        ? firstMessage(Object.values(body)[0])
        : null

export const errorMessage = error => {
  if (!error.response) return "Server se nepodařilo zastihnout."
  if (error.response.status === 400 && firstMessage(error.response.data))
    return firstMessage(error.response.data)
  return `Server odpověděl chybou ${error.response.status}.`
}

export const reportError = error => {
  message.error(errorMessage(error))
  console.error(error)
}

export const reportRejected = () =>
  message.error("Server jeden záznam odmítl. Zůstává v telefonu, dej vědět správci.")
