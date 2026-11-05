<script setup>
import { computed, inject, onBeforeUnmount, ref, watch } from "vue"
import { Marker } from "maplibre-gl"

import BoxMarkers from "@/components/map/BoxMarkers.vue"
import {
  boundsOf,
  bubbleDiameter,
  clusterByDistance,
  FIT_PADDING,
  inView,
  MERGE_GAP,
} from "@/components/map/geometry.js"
import { areaBubbleElement, boxMarkerElement } from "@/components/map/markers.js"

// From here in, every box has room for its own marker and name
const CLUSTER_UNTIL_ZOOM = 14

const props = defineProps({
  // [{ id, name, location: GeoJSON Point, state: one of BOX_STATES, area_id }]
  boxes: { type: Array, required: true },
  selectedId: { type: String, default: null },
  // area id → name, which labels a bubble of one area's boxes
  areaNames: { type: Map, required: true },
})

// The id of a lone box; a cluster zooms in instead
const emit = defineEmits(["select"])

const { map } = inject("map")
const zoom = ref(map.value.getZoom())
// A pan brings other clusters into view, see inView
const moved = ref(0)
const onMove = () => {
  zoom.value = map.value.getZoom()
  moved.value += 1
}
map.value.on("moveend", onMove)
map.value.on("resize", onMove)

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
    selected: items.some(box => box.id === props.selectedId),
  })
}

const render = () => {
  clear()
  if (!clustered.value) return
  const points = props.boxes.map(box => {
    const { x, y } = map.value.project(box.location.coordinates)
    return { x, y, weight: 1, box }
  })
  const visible = inView(map.value)
  markers = clusterByDistance(points, MERGE_GAP)
    .filter(visible)
    .map(cluster => {
      const items = cluster.items.map(item => item.box)
      const [box] = items
      const element =
        items.length > 1
          ? clusterElement(items)
          : boxMarkerElement({
              state: box.state,
              selected: box.id === props.selectedId,
            })
      element.addEventListener("click", event => {
        event.stopPropagation()
        if (items.length > 1)
          map.value.fitBounds(boundsOf(items.map(item => item.location)), {
            padding: FIT_PADDING,
          })
        else emit("select", box.id)
      })
      return new Marker({ element, anchor: "center" })
        .setLngLat(map.value.unproject([cluster.x, cluster.y]))
        .addTo(map.value)
    })
}

watch([() => props.boxes, () => props.selectedId, moved], render, { immediate: true })

onBeforeUnmount(() => {
  map.value.off("moveend", onMove)
  map.value.off("resize", onMove)
  clear()
})
</script>

<template>
  <BoxMarkers
    v-if="!clustered"
    :boxes="boxes"
    :selected-id="selectedId"
    @select="emit('select', $event)"
  />
</template>
