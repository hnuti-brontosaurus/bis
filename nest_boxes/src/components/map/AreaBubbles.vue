<script setup>
import { inject, onBeforeUnmount, ref, watch } from "vue"
import { LngLatBounds, Marker } from "maplibre-gl"

import { bubbleDiameter, clusterByDistance } from "@/components/map/geometry.js"
import { areaBubbleElement } from "@/components/map/markers.js"
import { areaCountLabel } from "@/composables/czech.js"

const MERGE_DISTANCE = 50

const props = defineProps({
  // PublicArea[] with a marker, see data/public.js
  areas: { type: Array, required: true },
  selectedId: { type: Number, default: null },
})

const emit = defineEmits(["select"])

const { map } = inject("map")
const zoom = ref(map.value.getZoom())
const onZoom = () => (zoom.value = map.value.getZoom())
map.value.on("zoomend", onZoom)

let markers = []

const clear = () => {
  markers.forEach(marker => marker.remove())
  markers = []
}

const clusterBounds = cluster =>
  cluster.items.reduce(
    (bounds, item) => bounds.extend(item.area.marker.coordinates),
    new LngLatBounds(),
  )

const render = () => {
  const points = props.areas.map(area => {
    const { x, y } = map.value.project(area.marker.coordinates)
    return { x, y, weight: area.box_count, area }
  })
  clear()
  markers = clusterByDistance(points, MERGE_DISTANCE).map(cluster => {
    const [biggest] = cluster.items
    const merged = cluster.items.length > 1
    const element = areaBubbleElement({
      count: cluster.weight,
      diameter: bubbleDiameter(cluster.weight),
      name: biggest.area.name,
      extra: merged ? `· ${areaCountLabel(cluster.items.length)}` : "",
      merged,
      selected: cluster.items.some(item => item.area.id === props.selectedId),
    })
    element.addEventListener("click", () => {
      if (merged)
        map.value.fitBounds(clusterBounds(cluster), { padding: 120, maxZoom: 13 })
      else emit("select", biggest.area)
    })
    return new Marker({ element, anchor: "center" })
      .setLngLat(map.value.unproject([cluster.x, cluster.y]))
      .addTo(map.value)
  })
}

watch([() => props.areas, () => props.selectedId, zoom], render, { immediate: true })

onBeforeUnmount(() => {
  map.value.off("zoomend", onZoom)
  clear()
})
</script>

<template>
  <span hidden />
</template>
