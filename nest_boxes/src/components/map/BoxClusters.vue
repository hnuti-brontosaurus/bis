<script setup>
import { computed, inject, onBeforeUnmount, ref, watch } from "vue"
import { Marker } from "maplibre-gl"

import BoxMarkers from "@/components/map/BoxMarkers.vue"
import {
  boundsOf,
  bubbleDiameter,
  CLUSTER_UNTIL_ZOOM,
  clusterByDistance,
  FIT_PADDING,
  inView,
  MERGE_GAP,
} from "@/components/map/geometry.js"
import { areaBubbleElement, boxMarkerElement } from "@/components/map/markers.js"

const props = defineProps({
  // [{ id, name, location: GeoJSON Point, state: one of BOX_STATES, area_id }]
  boxes: { type: Array, required: true },
  selectedId: { type: String, default: null },
  pickedIds: { type: Array, default: () => [] },
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

const isSelected = box =>
  box.id === props.selectedId || props.pickedIds.includes(box.id)

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
    selected: items.some(isSelected),
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
              selected: isSelected(box),
            })
      element.addEventListener("click", event => {
        event.stopPropagation()
        if (items.length > 1)
          map.value.fitBounds(boundsOf(items.map(item => item.location)), {
            padding: FIT_PADDING,
          })
        else emit("select", box.id, event.shiftKey)
      })
      return new Marker({ element, anchor: "center" })
        .setLngLat(map.value.unproject([cluster.x, cluster.y]))
        .addTo(map.value)
    })
}

watch(
  [() => props.boxes, () => props.selectedId, () => props.pickedIds, moved],
  render,
  {
    immediate: true,
  },
)

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
    :picked-ids="pickedIds"
    @select="(id, shift) => emit('select', id, shift)"
  />
</template>
