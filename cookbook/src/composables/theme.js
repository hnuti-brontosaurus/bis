import { computed, ref, toRef } from "vue"
import { darkTheme, lightTheme, useMessage } from "naive-ui"
import {
  createSharedComposable,
  toRefs,
  useLocalStorage,
  useStorage,
  useThrottleFn,
} from "@vueuse/core"
import axios from "axios"
import { settings, useDarkTheme } from "@/composables/settings.js"

const primary = "#239d46"
const lighter = "#39a759"
const darker = "#208d3f"

function scale(str, factor = 1.4) {
  if (typeof str !== "string") return str
  return str.replace(/-?\d+(?:\.\d+)?px/g, m => {
    const n = Number.parseFloat(m)
    const v = n * factor
    const r = Math.floor(v)
    return `${r}px`
  })
}

export const baseTheme = computed(() => (useDarkTheme.value ? darkTheme : lightTheme))

export const theme = computed(() => {
  const data = {}

  const scaleEntry = (name, values) => {
    data[name] = Object.fromEntries(
      Object.entries(values).map(([key, value]) => [key, scale(value)]),
    )
  }

  Object.entries(baseTheme.value).forEach(([name, entry]) => {
    if (!["common", "name"].includes(name)) {
      if (entry.self === undefined) return
      entry = entry.self(baseTheme.value.common)
    }
    scaleEntry(name, entry)
  })

  data.common.fontFamily = '"Delm", "Segoe UI", Tahoma, Geneva, Verdana, sans-serif'
  data.common.borderRadius = "10px"
  data.common.borderRadiusSmall = "10px"
  data.common.primaryColor = primary
  data.common.primaryColorHover = useDarkTheme.value ? lighter : darker
  data.common.primaryColorPressed = useDarkTheme.value ? darker : lighter
  data.common.primaryColorSuppl = useDarkTheme.value ? lighter : darker
  data.PageHeader.titleFontSize = scale(data.common.fontSizeHuge, 2)
  data.PageHeader.titleTextColor = data.common.textColorPrimary
  data.Button.iconSizeSmall = data.Button.iconSizeTiny
  data.Button.iconSizeTiny = scale(data.Button.iconSizeTiny, 0.8)

  return data
})
