import { computed, watchEffect } from "vue"
import { darkTheme, lightTheme } from "naive-ui"

import { useDarkTheme } from "@/composables/settings.js"

const palettes = {
  light: {
    background: "#ebe7dc",
    surface: "#f8f5ec",
    surfaceMuted: "#e0dbcc",
    line: "#cfc7b3",
    text: "#29251e",
    muted: "#6c6455",
    primary: "#1e7f3f",
    primaryHover: "#176a33",
    primaryPressed: "#125a2b",
    primaryInk: "#ffffff",
    primarySoft: "#d6e6d2",
    primaryText: "#186e35",
    accent: "#f07832",
    accentInk: "#2b1303",
    accentSoft: "#f7dcc6",
    accentText: "#b04d12",
    info: "#377d69",
    danger: "#b3263f",
    warningText: "#7d3a0c",
    warningLine: "#e6a877",
    headerLine: "#29251e",
    switchRail: "#6c6455",
    hoverShadow: "0 8px 20px rgba(60, 45, 20, 0.16)",
  },
  dark: {
    background: "#1b1713",
    surface: "#25201a",
    surfaceMuted: "#302920",
    line: "#453b2e",
    text: "#eee6d7",
    muted: "#a99c87",
    primary: "#4db56c",
    primaryHover: "#63c881",
    primaryPressed: "#3fa05d",
    primaryInk: "#07200f",
    primarySoft: "#24382a",
    primaryText: "#6fcb8b",
    accent: "#f58a4b",
    accentInk: "#2b1303",
    accentSoft: "#46291a",
    accentText: "#f8a673",
    info: "#6fb5a2",
    danger: "#ff7d8f",
    warningText: "#f8c29d",
    warningLine: "#70422a",
    headerLine: "#a99c87",
    switchRail: "#5a4d3c",
    hoverShadow: "0 8px 20px rgba(0, 0, 0, 0.5)",
  },
}

const fonts = {
  display: '"Bitter", Georgia, serif',
  body: '"Source Sans 3", "Segoe UI", Tahoma, Geneva, Verdana, sans-serif',
}

const SCALE = 1.2

function scale(str, factor = SCALE) {
  if (typeof str !== "string") return str
  return str.replace(/-?\d+(?:\.\d+)?px/g, m => {
    const n = Number.parseFloat(m)
    const v = n * factor
    const r = Math.floor(v)
    return `${r}px`
  })
}

const scaleEntry = values =>
  Object.fromEntries(Object.entries(values).map(([key, value]) => [key, scale(value)]))

const withAlpha = (hex, alpha) => {
  const channels = [1, 3, 5].map(start =>
    Number.parseInt(hex.slice(start, start + 2), 16),
  )
  return `rgba(${channels.join(", ")}, ${alpha})`
}

const allStates = (name, color, hover = color, pressed = color) => ({
  [name]: color,
  [`${name}Hover`]: hover,
  [`${name}Pressed`]: pressed,
  [`${name}Suppl`]: hover,
})

const commonFor = (base, colors) => ({
  ...base,
  ...allStates(
    "primaryColor",
    colors.primary,
    colors.primaryHover,
    colors.primaryPressed,
  ),
  ...allStates(
    "successColor",
    colors.primary,
    colors.primaryHover,
    colors.primaryPressed,
  ),
  ...allStates("infoColor", colors.info),
  ...allStates("warningColor", colors.accent),
  ...allStates("errorColor", colors.danger),
  baseColor: colors.primaryInk,
  bodyColor: colors.background,
  cardColor: colors.surface,
  modalColor: colors.surface,
  popoverColor: colors.surface,
  tableColor: colors.surface,
  inputColor: colors.surface,
  inputColorDisabled: colors.surfaceMuted,
  tagColor: colors.surfaceMuted,
  actionColor: colors.surfaceMuted,
  tableHeaderColor: colors.surfaceMuted,
  tabColor: colors.surfaceMuted,
  avatarColor: colors.surfaceMuted,
  codeColor: colors.surfaceMuted,
  textColorBase: colors.text,
  textColor1: colors.text,
  textColor2: colors.text,
  textColor3: colors.muted,
  textColorDisabled: withAlpha(colors.muted, 0.6),
  placeholderColor: withAlpha(colors.muted, 0.75),
  placeholderColorDisabled: withAlpha(colors.muted, 0.5),
  iconColor: colors.muted,
  iconColorHover: colors.text,
  iconColorPressed: colors.text,
  closeIconColor: colors.muted,
  closeIconColorHover: colors.text,
  closeIconColorPressed: colors.text,
  clearColor: colors.muted,
  clearColorHover: colors.text,
  clearColorPressed: colors.text,
  dividerColor: colors.line,
  borderColor: colors.line,
  railColor: colors.line,
  progressRailColor: colors.line,
  hoverColor: withAlpha(colors.text, 0.07),
  pressedColor: withAlpha(colors.text, 0.12),
  tableColorHover: withAlpha(colors.text, 0.04),
  tableColorStriped: withAlpha(colors.text, 0.03),
  buttonColor2: withAlpha(colors.text, 0.07),
  buttonColor2Hover: withAlpha(colors.text, 0.11),
  buttonColor2Pressed: withAlpha(colors.text, 0.15),
  fontFamily: fonts.body,
  fontWeightStrong: "600",
  borderRadius: "4px",
  borderRadiusSmall: "3px",
})

const dashed = color => `1px dashed ${color}`

const componentOverrides = colors => ({
  Layout: {
    color: colors.background,
    headerColor: colors.background,
    headerBorderColor: colors.headerLine,
    footerColor: colors.background,
    footerBorderColor: colors.line,
  },
  Card: {
    borderColor: colors.line,
    boxShadow: colors.hoverShadow,
    titleFontWeight: "700",
  },
  Button: {
    fontWeight: "600",
    color: colors.surface,
    colorHover: colors.surface,
    colorPressed: colors.surfaceMuted,
    colorFocus: colors.surface,
    textColorHover: colors.primaryText,
    textColorPressed: colors.primaryText,
    textColorFocus: colors.primaryText,
  },
  Tag: {
    color: "transparent",
    colorBordered: "transparent",
    colorBorderedPrimary: "transparent",
    colorBorderedWarning: "transparent",
    textColor: colors.muted,
    border: dashed(colors.line),
    colorPrimary: "transparent",
    textColorPrimary: colors.primaryText,
    borderPrimary: dashed(colors.primaryText),
    closeIconColorPrimary: colors.primaryText,
    closeIconColorHoverPrimary: colors.primaryText,
    closeIconColorPressedPrimary: colors.primaryText,
    colorWarning: "transparent",
    textColorWarning: colors.accentText,
    borderWarning: dashed(colors.accentText),
  },
  Alert: {
    colorWarning: colors.accentSoft,
    borderWarning: `1px solid ${colors.warningLine}`,
    titleTextColorWarning: colors.warningText,
    contentTextColorWarning: colors.warningText,
    iconColorWarning: colors.accentText,
  },
  Badge: { color: colors.accent },
  Input: { border: `1px solid ${colors.line}` },
  Select: {
    peers: {
      InternalSelection: { color: colors.surface, border: `1px solid ${colors.line}` },
    },
  },
  Switch: { railColor: colors.switchRail },
  DataTable: {
    thColor: "transparent",
    tdColor: "transparent",
    thFontWeight: "600",
  },
  Typography: { headerFontWeight: "700" },
  PageHeader: { titleFontWeight: "700", titleTextColor: colors.text },
  Tabs: { tabTextColorActiveLine: colors.primaryText, tabFontWeightActive: "600" },
})

export const baseTheme = computed(() => (useDarkTheme.value ? darkTheme : lightTheme))

export const palette = computed(() => palettes[useDarkTheme.value ? "dark" : "light"])

export const theme = computed(() => {
  const common = commonFor(baseTheme.value.common, palette.value)
  const overrides = componentOverrides(palette.value)
  const data = { common: scaleEntry(common) }

  Object.entries(baseTheme.value).forEach(([name, entry]) => {
    if (entry.self === undefined) return
    data[name] = scaleEntry({ ...entry.self(common), ...overrides[name] })
  })

  data.PageHeader.titleFontSize = scale(data.common.fontSizeHuge, 2)
  data.Button.iconSizeSmall = data.Button.iconSizeTiny
  data.Button.iconSizeTiny = scale(data.Button.iconSizeTiny, 0.8)

  return data
})

const cssVariableName = name =>
  `--${name.replace(/[A-Z]/g, letter => `-${letter.toLowerCase()}`)}`

watchEffect(() => {
  const { style } = document.documentElement
  Object.entries(palette.value).forEach(([name, value]) =>
    style.setProperty(cssVariableName(name), value),
  )
  style.setProperty("--font-display", fonts.display)
  style.setProperty("--font-body", fonts.body)
  style.colorScheme = useDarkTheme.value ? "dark" : "light"
})
