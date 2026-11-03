import { MAP_STYLE_URL } from "@/config.js"

let baseStyle = null

export const loadBaseStyle = () => {
  baseStyle ??= fetch(MAP_STYLE_URL).then(response => response.json())
  return baseStyle
}
