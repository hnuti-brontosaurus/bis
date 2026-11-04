<script setup>
import { inject, onBeforeUnmount, watch } from "vue"
import { Marker } from "maplibre-gl"

import { boxMarkerElement } from "@/components/map/markers.js"

const props = defineProps({
  // [{ id, name, location: GeoJSON Point, state: one of BOX_STATES }]
  boxes: { type: Array, required: true },
  selectedId: { type: [String, Number], default: null },
  // the zoom below which the names are hidden, for a map of many areas' boxes
  labelsZoom: { type: Number, default: 0 },
})

const emit = defineEmits(["select"])

const { map } = inject("map")
let markers = new Map()

const clear = () => {
  markers.forEach(marker => marker.remove())
  markers = new Map()
}

const showLabels = () =>
  map.value
    .getContainer()
    .classList.toggle("box-labels-hidden", map.value.getZoom() < props.labelsZoom)
map.value.on("zoomend", showLabels)
showLabels()

watch(
  () => props.boxes,
  boxes => {
    clear()
    for (const box of boxes) {
      const element = boxMarkerElement({
        name: box.name,
        state: box.state,
        selected: box.id === props.selectedId,
      })
      element.addEventListener("click", event => {
        event.stopPropagation()
        emit("select", box.id)
      })
      markers.set(
        box.id,
        new Marker({ element, anchor: "center" })
          .setLngLat(box.location.coordinates)
          .addTo(map.value),
      )
    }
  },
  { immediate: true },
)

watch(
  () => props.selectedId,
  (selected, previous) => {
    markers.get(previous)?.getElement().classList.remove("selected")
    markers.get(selected)?.getElement().classList.add("selected")
  },
)

onBeforeUnmount(() => {
  map.value.off("zoomend", showLabels)
  map.value.getContainer().classList.remove("box-labels-hidden")
  clear()
})
</script>

<template>
  <span hidden />
</template>
