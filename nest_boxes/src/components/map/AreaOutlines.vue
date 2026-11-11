<script setup>
import { inject, onBeforeUnmount, watchEffect } from "vue"

import { CLUSTER_UNTIL_ZOOM } from "@/components/map/geometry.js"

const props = defineProps({
  // [{ id, name, outline: GeoJSON }], see nest_boxes/outlines.py
  outlines: { type: Array, required: true },
})

const OVERLAY = "nest_boxes_area_outlines"
const FILL = `${OVERLAY}_fill`
// Only once boxes show one by one: further out, bubbles already group them
const SHOWN_FROM_ZOOM = CLUSTER_UNTIL_ZOOM

const { map, setOverlay, removeOverlay } = inject("map")

const opacity = (normal, hovered) => [
  "case",
  ["boolean", ["feature-state", "hover"], false],
  hovered,
  normal,
]

watchEffect(() => {
  const features = props.outlines.map(area => ({
    type: "Feature",
    id: area.id,
    properties: { name: area.name },
    geometry: area.outline,
  }))
  setOverlay(OVERLAY, colors => ({
    sources: {
      [OVERLAY]: { type: "geojson", data: { type: "FeatureCollection", features } },
    },
    layers: [
      {
        id: FILL,
        type: "fill",
        source: OVERLAY,
        minzoom: SHOWN_FROM_ZOOM,
        paint: {
          "fill-color": colors.primary,
          "fill-opacity": opacity(0.06, 0.18),
        },
      },
      {
        id: `${OVERLAY}_line`,
        type: "line",
        source: OVERLAY,
        minzoom: SHOWN_FROM_ZOOM,
        paint: {
          "line-color": colors.primary,
          "line-opacity": opacity(0.45, 0.9),
          "line-width": 1.25,
        },
      },
      {
        id: `${OVERLAY}_label`,
        type: "symbol",
        source: OVERLAY,
        minzoom: SHOWN_FROM_ZOOM,
        layout: {
          "text-field": ["get", "name"],
          "text-font": ["Noto Sans Bold"],
          "text-size": 12,
        },
        paint: {
          "text-color": colors.primaryText,
          "text-halo-color": colors.surface,
          "text-halo-width": 1.5,
          "text-opacity": opacity(0.6, 1),
        },
      },
    ],
  }))
})

let hovered = null

const setHovered = id => {
  if (hovered !== null)
    map.value.setFeatureState({ source: OVERLAY, id: hovered }, { hover: false })
  hovered = id
  if (hovered !== null)
    map.value.setFeatureState({ source: OVERLAY, id: hovered }, { hover: true })
}

const onMove = event => {
  const id = event.features[0].id
  if (id !== hovered) setHovered(id)
}
const onLeave = () => setHovered(null)

map.value.on("mousemove", FILL, onMove)
map.value.on("mouseleave", FILL, onLeave)

onBeforeUnmount(() => {
  map.value.off("mousemove", FILL, onMove)
  map.value.off("mouseleave", FILL, onLeave)
  removeOverlay(OVERLAY)
})
</script>

<template>
  <span hidden />
</template>
