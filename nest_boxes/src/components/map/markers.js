import { icons } from "@/assets/icons.js"

export const BOX_STATES = ["todo", "done", "not_found", "out"]

const GLYPH_ICONS = { done: "check", not_found: "q" }

export const glyphMarkup = state =>
  GLYPH_ICONS[state]
    ? `<svg class="marker-icon" viewBox="0 0 24 24" aria-hidden="true">${icons[GLYPH_ICONS[state]]}</svg>`
    : ""

const element = (className, html = "") => {
  const node = document.createElement("div")
  node.className = className
  node.innerHTML = html
  return node
}

export const boxMarkerElement = ({ name, state, selected }) => {
  const node = element(`box-marker ${state}${selected ? " selected" : ""}`)
  node.append(element("dot", glyphMarkup(state)))
  const label = element("label")
  label.textContent = name
  node.append(label)
  return node
}

export const planLabelElement = name => {
  const node = element("plan-label")
  node.textContent = name || "plán"
  return node
}

export const areaBubbleElement = ({
  count,
  diameter,
  name,
  extra,
  merged,
  selected,
}) => {
  const node = element(
    `area-bubble${merged ? " merged" : ""}${selected ? " selected" : ""}`,
  )
  node.style.setProperty("--d", `${diameter}px`)
  const bubble = element("bubble")
  bubble.textContent = count
  const label = element("label")
  label.textContent = name
  if (extra) {
    const small = document.createElement("small")
    small.textContent = extra
    label.append(small)
  }
  node.append(bubble, label)
  return node
}
