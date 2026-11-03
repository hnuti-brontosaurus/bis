import { computed, watchEffect } from "vue"
import { darkTheme, lightTheme } from "naive-ui"
import { usePreferredDark, useStorage } from "@vueuse/core"

export const palettes = {
  light: {
    bg: "#f0f4f1",
    surface: "#fcfdfc",
    surface2: "#e9f0eb",
    line: "#dce5df",
    lineStrong: "#bfcbc3",
    text: "#36423b",
    muted: "#66756c",
    primary: "#118a2c",
    primaryStrong: "#0b6420",
    primaryInk: "#ffffff",
    primarySoft: "#ddf2e3",
    primaryText: "#0d7425",
    accent: "#3b6a80",
    accentInk: "#ffffff",
    accentSoft: "#dbe7ec",
    danger: "#b8494a",
    dangerSoft: "#f4dcdb",
    lime: "#afcd32",
    limeInk: "#173a26",
    warn: "#7a6418",
    warnSoft: "#f6eecb",
    info: "#3b6a80",
    infoSoft: "#dbe7ec",
    loc: "#2a7de1",
    locRing: "rgba(42, 125, 225, 0.22)",
    planBg: "rgba(46, 143, 69, 0.09)",
    shadowC: "rgba(0, 0, 0, 0.14)",
    cardShadow: "0 1px 2px rgba(30, 60, 40, 0.05)",
    logo: "#118a2c",
    map: {
      out: "#dfe7e1",
      land: "#edf2ec",
      field: "#e5ede1",
      forest: "#cfe3d2",
      forestLine: "#b8d4bd",
      water: "#a3c9d8",
      road: "#f8fbf8",
      roadCase: "#c9d4cc",
      path: "#85948b",
      contour: "#cdd8cf",
      bld: "#dbe3dd",
      label: "#3f5a4c",
      border: "#118a2c",
      city: "#3f5a4c",
    },
    mk: {
      nf: "#87938c",
      nfInk: "#ffffff",
      out: "#a2ada6",
    },
  },
  dark: {
    bg: "#101613",
    surface: "#18211c",
    surface2: "#202a24",
    line: "#2e3c34",
    lineStrong: "#506258",
    text: "#eef4f0",
    muted: "#b2bfb6",
    primary: "#55bf70",
    primaryStrong: "#9de2af",
    primaryInk: "#0a1d10",
    primarySoft: "#22412b",
    primaryText: "#9de2af",
    accent: "#a3c7d8",
    accentInk: "#13293a",
    accentSoft: "#2b3d45",
    danger: "#f0968f",
    dangerSoft: "#47302c",
    lime: "#afcd32",
    limeInk: "#173a26",
    warn: "#e2ca84",
    warnSoft: "#3e3a26",
    info: "#a3c7d8",
    infoSoft: "#2b3d45",
    loc: "#5b9ee6",
    locRing: "rgba(42, 125, 225, 0.22)",
    planBg: "rgba(80, 180, 105, 0.14)",
    shadowC: "rgba(0, 0, 0, 0.4)",
    cardShadow: "none",
    // The primary green is too dark against the dark header.
    logo: "#9de2af",
    map: {
      out: "#101613",
      land: "#18201b",
      field: "#202a24",
      forest: "#24392a",
      forestLine: "#2e3c34",
      water: "#2f5865",
      road: "#506258",
      roadCase: "#101613",
      path: "#b2bfb6",
      contour: "#2e3c34",
      bld: "#2e3c34",
      label: "#d8e3dc",
      border: "#55bf70",
      city: "#d8e3dc",
    },
    mk: {
      nf: "#7f8d85",
      nfInk: "#ffffff",
      out: "#64736b",
    },
  },
}

export const shape = {
  radius: "12px",
  radiusButton: "8px",
  radiusChip: "999px",
  radiusInput: "8px",
}

export const font = '"Karla", sans-serif'

const themePreference = useStorage("nest_boxes_theme", "")
const systemPrefersDark = usePreferredDark()

export const isDark = computed(() =>
  themePreference.value ? themePreference.value === "dark" : systemPrefersDark.value,
)

export const toggleTheme = () => {
  themePreference.value = isDark.value ? "light" : "dark"
}

export const palette = computed(() => palettes[isDark.value ? "dark" : "light"])

export const baseTheme = computed(() => (isDark.value ? darkTheme : lightTheme))

const channels = hex =>
  [1, 3, 5].map(start => Number.parseInt(hex.slice(start, start + 2), 16))

export const withAlpha = (hex, alpha) => `rgba(${channels(hex).join(", ")}, ${alpha})`

export const mix = (from, to, weight) => {
  const target = channels(to)
  return `#${channels(from)
    .map((channel, index) =>
      Math.round(channel + (target[index] - channel) * weight)
        .toString(16)
        .padStart(2, "0"),
    )
    .join("")}`
}

const allStates = (name, color, hover, pressed) => ({
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
    mix(colors.primary, colors.primaryStrong, 0.3),
    colors.primaryStrong,
  ),
  ...allStates(
    "successColor",
    colors.primary,
    mix(colors.primary, colors.primaryStrong, 0.3),
    colors.primaryStrong,
  ),
  ...allStates("infoColor", colors.info, colors.info, colors.info),
  ...allStates("warningColor", colors.warn, colors.warn, colors.warn),
  ...allStates("errorColor", colors.danger, colors.danger, colors.danger),
  baseColor: colors.primaryInk,
  bodyColor: colors.bg,
  cardColor: colors.surface,
  modalColor: colors.surface,
  popoverColor: colors.surface,
  tableColor: colors.surface,
  inputColor: colors.surface,
  inputColorDisabled: colors.surface2,
  tagColor: colors.surface2,
  actionColor: colors.surface2,
  tableHeaderColor: colors.surface2,
  tabColor: colors.surface2,
  avatarColor: colors.primarySoft,
  textColorBase: colors.text,
  textColor1: colors.text,
  textColor2: colors.text,
  textColor3: colors.muted,
  textColorDisabled: withAlpha(colors.muted, 0.6),
  placeholderColor: withAlpha(colors.muted, 0.8),
  placeholderColorDisabled: withAlpha(colors.muted, 0.5),
  iconColor: colors.muted,
  iconColorHover: colors.text,
  iconColorPressed: colors.text,
  dividerColor: colors.line,
  borderColor: colors.lineStrong,
  railColor: colors.lineStrong,
  progressRailColor: colors.surface2,
  hoverColor: withAlpha(colors.text, 0.06),
  pressedColor: withAlpha(colors.text, 0.1),
  tableColorHover: withAlpha(colors.text, 0.04),
  buttonColor2: withAlpha(colors.text, 0.06),
  buttonColor2Hover: withAlpha(colors.text, 0.1),
  buttonColor2Pressed: withAlpha(colors.text, 0.14),
  fontFamily: font,
  fontWeightStrong: "700",
  borderRadius: shape.radiusButton,
  borderRadiusSmall: "6px",
})

const componentOverrides = colors => ({
  Card: {
    borderRadius: shape.radius,
    borderColor: colors.line,
    titleFontWeight: "800",
  },
  Button: {
    fontWeight: "700",
    textColorPrimary: colors.primaryInk,
    textColorHoverPrimary: colors.primaryInk,
    textColorPressedPrimary: colors.primaryInk,
    textColorFocusPrimary: colors.primaryInk,
    color: colors.surface,
    border: `1px solid ${colors.lineStrong}`,
  },
  Tag: {
    borderRadius: shape.radiusChip,
    border: "0",
    color: colors.surface2,
    textColor: colors.muted,
    colorPrimary: colors.primarySoft,
    textColorPrimary: colors.primaryText,
    colorWarning: colors.warnSoft,
    textColorWarning: colors.warn,
    colorError: colors.dangerSoft,
    textColorError: colors.danger,
    colorInfo: colors.infoSoft,
    textColorInfo: colors.info,
  },
  Input: {
    borderRadius: shape.radiusInput,
    border: `1px solid ${colors.lineStrong}`,
    borderFocus: `1px solid ${colors.primary}`,
    boxShadowFocus: `0 0 0 3px ${colors.primarySoft}`,
  },
  Select: {
    peers: {
      InternalSelection: {
        borderRadius: shape.radiusInput,
        color: colors.surface,
        border: `1px solid ${colors.lineStrong}`,
      },
    },
  },
  Badge: { color: colors.accent, textColor: colors.accentInk },
  DataTable: {
    thColor: "transparent",
    tdColor: "transparent",
    thTextColor: colors.muted,
    thFontWeight: "700",
    borderColor: colors.line,
  },
  Drawer: { color: colors.surface },
  Tabs: { tabTextColorActiveLine: colors.text, barColor: colors.primary },
})

export const theme = computed(() => {
  const common = commonFor(baseTheme.value.common, palette.value)
  const overrides = componentOverrides(palette.value)
  const data = { common }

  Object.entries(baseTheme.value).forEach(([name, entry]) => {
    if (entry.self === undefined) return
    data[name] = { ...entry.self(common), ...overrides[name] }
  })

  return data
})

const kebab = name => name.replace(/([a-z])([A-Z0-9])/g, "$1-$2").toLowerCase()

export const cssVariables = colors =>
  Object.fromEntries(
    Object.entries(colors).flatMap(([name, value]) =>
      typeof value === "object"
        ? Object.entries(value).map(([key, nested]) => [
            `--${name}-${kebab(key)}`,
            nested,
          ])
        : [[`--${kebab(name)}`, value]],
    ),
  )

const constantVariables = {
  "--r": shape.radius,
  "--r-btn": shape.radiusButton,
  "--r-chip": shape.radiusChip,
  "--r-in": shape.radiusInput,
  "--font": font,
}

watchEffect(() => {
  const { style } = document.documentElement
  Object.entries({ ...cssVariables(palette.value), ...constantVariables }).forEach(
    ([name, value]) => style.setProperty(name, value),
  )
  style.colorScheme = isDark.value ? "dark" : "light"
})
