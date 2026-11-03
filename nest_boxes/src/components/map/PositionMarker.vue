<script setup>
import { inject, onBeforeUnmount, watch } from "vue"
import { Marker } from "maplibre-gl"

const props = defineProps({
  // GeoJSON point or null
  position: { type: Object, default: null },
})

const { map } = inject("map")
const element = document.createElement("div")
element.className = "position-marker"
const marker = new Marker({ element, anchor: "center" })

watch(
  () => props.position,
  position => {
    if (!position) return marker.remove()
    marker.setLngLat(position.coordinates).addTo(map.value)
  },
  { immediate: true },
)

onBeforeUnmount(() => marker.remove())
</script>

<template>
  <span hidden />
</template>
