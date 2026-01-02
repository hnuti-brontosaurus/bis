import { useLocalStorage } from "@vueuse/core"

const settings = useLocalStorage(
  "settings",
  {
    darkTheme: true,
    sidebarCollapsed: false,
  },
  { mergeDefaults: true },
)

const segmentations = useLocalStorage(
  "segmentationsSettings",
  {
    pageSize: 5,
  },
  { mergeDefaults: true },
)
const actions = useLocalStorage(
  "actionsSettings",
  {
    pageSize: 5,
    expanded: [],
    showLabels: true,
    minColumnWidth: 350,
  },
  { mergeDefaults: true },
)

export function useSettings() {
  return { settings, segmentations, actions }
}
