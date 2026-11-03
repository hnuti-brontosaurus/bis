import { nextTick } from "vue"
import { describe, expect, it } from "vitest"

import {
  cssVariables,
  isDark,
  mix,
  palette,
  palettes,
  theme,
  toggleTheme,
  withAlpha,
} from "@/composables/theme.js"

const flatten = colors => Object.values(cssVariables(colors))

describe("palettes", () => {
  it("define the same tokens in both themes", () => {
    expect(Object.keys(cssVariables(palettes.dark))).toEqual(
      Object.keys(cssVariables(palettes.light)),
    )
  })

  it("use only colours naive-ui can parse", () => {
    const colours = [...flatten(palettes.light), ...flatten(palettes.dark)].filter(
      value => value !== "none" && !value.includes(" 1px"),
    )
    colours
      .filter(value => !value.startsWith("0 "))
      .forEach(value => expect(value).toMatch(/^(#[0-9a-f]{6}|rgba\([\d., ]+\))$/))
  })

  it("name the css variables as visual-design.md does", () => {
    const names = Object.keys(cssVariables(palettes.light))
    expect(names).toEqual(
      expect.arrayContaining([
        "--bg",
        "--surface-2",
        "--line-strong",
        "--primary-ink",
        "--shadow-c",
        "--loc-ring",
        "--plan-bg",
        "--map-forest-line",
        "--map-road-case",
        "--mk-attn",
        "--mk-attn-ink",
        "--mk-out",
      ]),
    )
  })

  it("keep Light forest 1 and Forest 3 values", () => {
    expect(palettes.light.primary).toBe("#118a2c")
    expect(palettes.dark.bg).toBe("#101613")
    expect(palettes.dark.map.water).toBe("#2f5865")
  })
})

describe("colour helpers", () => {
  it("mix two hex colours", () => {
    expect(mix("#000000", "#ffffff", 0.5)).toBe("#808080")
    expect(mix("#118a2c", "#0b6420", 0)).toBe("#118a2c")
  })

  it("add alpha to a hex colour", () => {
    expect(withAlpha("#118a2c", 0.5)).toBe("rgba(17, 138, 44, 0.5)")
  })
})

describe("theme", () => {
  it("follows the system until toggled, then remembers the choice", async () => {
    expect(isDark.value).toBe(false)
    toggleTheme()
    await nextTick()
    expect(isDark.value).toBe(true)
    expect(localStorage.getItem("nest_boxes_theme")).toBe("dark")
    expect(palette.value).toBe(palettes.dark)
    toggleTheme()
    await nextTick()
    expect(localStorage.getItem("nest_boxes_theme")).toBe("light")
  })

  it("writes the palette onto <html>", () => {
    const style = document.documentElement.style
    expect(style.getPropertyValue("--primary")).toBe(palette.value.primary)
    expect(style.getPropertyValue("--map-land")).toBe(palette.value.map.land)
  })

  it("puts dark text on the light green buttons of the dark theme", () => {
    toggleTheme()
    expect(isDark.value).toBe(true)
    expect(theme.value.common.primaryColor).toBe(palettes.dark.primary)
    expect(theme.value.Button.textColorPrimary).toBe(palettes.dark.primaryInk)
  })
})
