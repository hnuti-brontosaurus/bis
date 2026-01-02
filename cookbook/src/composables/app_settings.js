import { useLocalStorage, useWindowSize } from "@vueuse/core"
import { computed, ref } from "vue"

const settings = useLocalStorage(
  "app_settings",
  {
    useDarkTheme: !!import.meta.env.VITE_DEFAULT_THEME_DARK,
    minColumnWidth: 350,
  },
  { mergeDefaults: true },
)

const contentWidth = ref(null)

export function useAppSettings() {
  const { width } = useWindowSize()

  const cols = computed(() => (min_column_width, max_width) => {
    max_width = max_width ?? contentWidth.value ?? width.value
    min_column_width = min_column_width ?? settings.value.minColumnWidth

    if (max_width < min_column_width) return 2
    if (max_width < min_column_width * 2) return 4
    if (max_width < min_column_width * 4) return 8
    return 16
  })

  return { settings, cols, contentWidth }
}
