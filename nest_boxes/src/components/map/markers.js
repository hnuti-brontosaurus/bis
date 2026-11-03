import { icons } from "@/assets/icons.js"
import { formatNumber } from "@/composables/czech.js"

// The season states of nest_boxes/models.py, and "out" for a box outside the batch
export const BOX_STATES = ["planned", "to_check", "attention", "done", "out"]

const GLYPH_ICONS = { done: "check", attention: "bang" }

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

/** A donut of the area's season states around its box count, or just the count when `plain`. */
export const areaBubbleElement = ({
  plain,
  count,
  done,
  attention,
  diameter,
  name,
  extra,
  merged,
  selected,
}) => {
  const node = element(
    `area-bubble${plain ? " plain" : ""}${merged ? " merged" : ""}${selected ? " selected" : ""}`,
  )
  node.style.setProperty("--d", `${diameter}px`)
  const share = value => `${count ? (value / count) * 100 : 0}%`
  node.style.setProperty("--done", share(done))
  node.style.setProperty("--attention", share(done + attention))
  const bubble = element("bubble")
  const number = document.createElement("b")
  number.textContent = formatNumber(count)
  bubble.append(number)
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
