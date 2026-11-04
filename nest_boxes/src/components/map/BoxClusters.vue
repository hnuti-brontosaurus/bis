<script setup>
import { computed, inject, onBeforeUnmount, ref, watch } from "vue"
import { Marker } from "maplibre-gl"

import BoxMarkers from "@/components/map/BoxMarkers.vue"
import {
  bubbleDiameter,
  clusterByDistance,
  MERGE_GAP,
} from "@/components/map/geometry.js"
import { areaBubbleElement, boxMarkerElement } from "@/components/map/markers.js"

// From here in, every box has room for its own marker and name
const CLUSTER_UNTIL_ZOOM = 14

const props = defineProps({
  // [{ id, name, location: GeoJSON Point, state: one of BOX_STATES, area_id }]
  boxes: { type: Array, required: true },
  selectedIds: { type: Array, default: () => [] },
  // area id → name, which labels a bubble of one area's boxes
  areaNames: { type: Map, required: true },
})

// The ids of the boxes under the marker; the panel acts on them
const emit = defineEmits(["select"])

const { map } = inject("map")
const zoom = ref(map.value.getZoom())
const onZoom = () => (zoom.value = map.value.getZoom())
map.value.on("zoomend", onZoom)

const clustered = computed(() => zoom.value < CLUSTER_UNTIL_ZOOM)

let markers = []

const clear = () => {
  markers.forEach(marker => marker.remove())
  markers = []
}

const clusterElement = items => {
  const count = state => items.filter(box => box.state === state).length
  const areaIds = new Set(items.map(box => box.area_id))
  return areaBubbleElement({
    count: items.length,
    done: count("done"),
    attention: count("attention"),
    diameter: bubbleDiameter(items.length),
    name: areaIds.size === 1 ? props.areaNames.get(items[0].area_id) : "",
    merged: true,
    selected: items.some(box => props.selectedIds.includes(box.id)),
  })
}

const render = () => {
  clear()
  if (!clustered.value) return
  const points = props.boxes.map(box => {
    const { x, y } = map.value.project(box.location.coordinates)
    return { x, y, weight: 1, box }
  })
  markers = clusterByDistance(points, MERGE_GAP).map(cluster => {
    const items = cluster.items.map(item => item.box)
    const [box] = items
    const element =
      items.length > 1
        ? clusterElement(items)
        : boxMarkerElement({
            state: box.state,
            selected: props.selectedIds.includes(box.id),
          })
    element.addEventListener("click", event => {
      event.stopPropagation()
      emit(
        "select",
        items.map(item => item.id),
      )
    })
    return new Marker({ element, anchor: "center" })
      .setLngLat(map.value.unproject([cluster.x, cluster.y]))
      .addTo(map.value)
  })
}

watch([() => props.boxes, () => props.selectedIds, zoom], render, { immediate: true })

onBeforeUnmount(() => {
  map.value.off("zoomend", onZoom)
  clear()
})
</script>

<template>
  <BoxMarkers
    v-if="!clustered"
    :boxes="boxes"
    :selected-id="selectedIds.length === 1 ? selectedIds[0] : null"
    @select="emit('select', [$event])"
  />
</template>
