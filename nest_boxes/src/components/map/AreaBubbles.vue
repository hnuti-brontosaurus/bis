<script setup>
import { inject, onBeforeUnmount, ref, watch } from "vue"
import { Marker } from "maplibre-gl"

import {
  boundsOf,
  bubbleDiameter,
  clusterByDistance,
  FIT_PADDING,
  MERGE_GAP,
} from "@/components/map/geometry.js"
import { areaBubbleElement } from "@/components/map/markers.js"
import { areaCountLabel } from "@/composables/czech.js"

const props = defineProps({
  // [{ area: PublicArea with a marker, count, done, attention }], see
  // composables/statistics.js; the rest of `count` is still to check
  areas: { type: Array, required: true },
  selectedId: { type: Number, default: null },
})

// The id of the one area under the bubble; a merged bubble zooms in instead
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

const render = () => {
  const points = props.areas.map(item => {
    const { x, y } = map.value.project(item.area.marker.coordinates)
    return { x, y, weight: item.count, ...item }
  })
  clear()
  markers = clusterByDistance(points, MERGE_GAP).map(cluster => {
    const [biggest] = cluster.items
    const merged = cluster.items.length > 1
    const sum = key => cluster.items.reduce((total, item) => total + item[key], 0)
    const element = areaBubbleElement({
      count: cluster.weight,
      done: sum("done"),
      attention: sum("attention"),
      diameter: bubbleDiameter(cluster.weight),
      name: biggest.area.name,
      extra: merged ? `· ${areaCountLabel(cluster.items.length)}` : "",
      merged,
      selected: cluster.items.some(item => item.area.id === props.selectedId),
    })
    element.addEventListener("click", () =>
      merged
        ? map.value.fitBounds(boundsOf(cluster.items.map(item => item.area.marker)), {
            padding: FIT_PADDING,
          })
        : emit("select", biggest.area.id),
    )
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
