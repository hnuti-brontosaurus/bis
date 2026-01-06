import { useLocalStorage, usePreferredDark } from "@vueuse/core"
import { computed } from "vue"

export const settings = useLocalStorage(
  "settings",
  {
    darkTheme: null,
  },
  { mergeDefaults: true },
)

export const useDarkTheme = computed(
  () => settings.value.darkTheme ?? usePreferredDark().value,
)
