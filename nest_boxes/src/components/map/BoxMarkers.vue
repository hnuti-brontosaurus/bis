<script setup>
import { inject, onBeforeUnmount, watchEffect } from "vue"
import { Marker } from "maplibre-gl"

import { boxMarkerElement } from "@/components/map/markers.js"

const props = defineProps({
  // [{ id, name, location: GeoJSON Point, state: one of BOX_STATES }]
  boxes: { type: Array, required: true },
  selectedId: { type: [String, Number], default: null },
})

const emit = defineEmits(["select"])

const { map } = inject("map")
let markers = []

const clear = () => {
  markers.forEach(marker => marker.remove())
  markers = []
}

watchEffect(() => {
  clear()
  markers = props.boxes.map(box => {
    const element = boxMarkerElement({
      name: box.name,
      state: box.state,
      selected: box.id === props.selectedId,
    })
    element.addEventListener("click", event => {
      event.stopPropagation()
      emit("select", box.id)
    })
    return new Marker({ element, anchor: "center" })
      .setLngLat(box.location.coordinates)
      .addTo(map.value)
  })
})

onBeforeUnmount(clear)
</script>

<template>
  <span hidden />
</template>
