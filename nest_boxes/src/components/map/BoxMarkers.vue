<script setup>
import { inject, onBeforeUnmount, watch } from "vue"
import { Marker } from "maplibre-gl"

import { inView } from "@/components/map/geometry.js"
import { boxMarkerElement } from "@/components/map/markers.js"

const props = defineProps({
  // [{ id, name, location: GeoJSON Point, state: one of BOX_STATES }]
  boxes: { type: Array, required: true },
  selectedId: { type: [String, Number], default: null },
  // only to look at: a click goes through to the map, as on a location picker
  passive: { type: Boolean, default: false },
})

const emit = defineEmits(["select"])

const { map } = inject("map")
// Only the boxes in view have a marker, see inView
let markers = new Map()

const clear = () => {
  markers.forEach(marker => marker.remove())
  markers = new Map()
}

const markerOf = box => {
  const element = boxMarkerElement({
    name: box.name,
    state: box.state,
    selected: box.id === props.selectedId,
  })
  if (props.passive) element.style.pointerEvents = "none"
  else
    element.addEventListener("click", event => {
      event.stopPropagation()
      emit("select", box.id)
    })
  return new Marker({ element, anchor: "center" })
    .setLngLat(box.location.coordinates)
    .addTo(map.value)
}

const sync = () => {
  const visible = inView(map.value)
  const shown = new Set()
  for (const box of props.boxes) {
    if (!visible(map.value.project(box.location.coordinates))) continue
    shown.add(box.id)
    if (!markers.has(box.id)) markers.set(box.id, markerOf(box))
  }
  for (const [id, marker] of markers)
    if (!shown.has(id)) {
      marker.remove()
      markers.delete(id)
    }
}

watch(
  () => props.boxes,
  () => {
    clear()
    sync()
  },
  { immediate: true },
)
// A resize changes the view too, and the map is resized while it settles in
map.value.on("moveend", sync)
map.value.on("resize", sync)

watch(
  () => props.selectedId,
  (selected, previous) => {
    markers.get(previous)?.getElement().classList.remove("selected")
    markers.get(selected)?.getElement().classList.add("selected")
  },
)

onBeforeUnmount(() => {
  map.value.off("moveend", sync)
  map.value.off("resize", sync)
  clear()
})
</script>

<template>
  <span hidden />
</template>
