<script setup>
import { inject, onBeforeUnmount, watch } from "vue"
import { Marker } from "maplibre-gl"

import { boxMarkerElement } from "@/components/map/markers.js"

const props = defineProps({
  // [{ id, name, location: GeoJSON Point, state: one of BOX_STATES }]
  boxes: { type: Array, required: true },
  selectedId: { type: [String, Number], default: null },
})

const emit = defineEmits(["select"])

const { map } = inject("map")
let markers = new Map()

const clear = () => {
  markers.forEach(marker => marker.remove())
  markers = new Map()
}

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

onBeforeUnmount(clear)
</script>

<template>
  <span hidden />
</template>
