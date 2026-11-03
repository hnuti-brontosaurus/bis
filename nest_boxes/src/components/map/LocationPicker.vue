<script setup>
import { computed, onBeforeUnmount, ref, shallowRef, watch } from "vue"
import { Marker } from "maplibre-gl"
import { NButton, useMessage } from "naive-ui"

import AppIcon from "@/components/app/AppIcon.vue"
import BaseMap from "@/components/map/BaseMap.vue"
import { boxMarkerElement } from "@/components/map/markers.js"
import { aroundPoint } from "@/components/map/geometry.js"

const props = defineProps({
  // Where the map starts when there is no location yet
  center: { type: Object, required: true },
  name: { type: String, default: "" },
  // Asks the phone for its position as soon as the picker opens
  locateOnOpen: { type: Boolean, default: false },
})

// GeoJSON point or null
const location = defineModel({ type: Object, default: null })

const message = useMessage()
const map = shallowRef(null)
const accuracy = ref(null)
const locating = ref(false)
let marker = null

const bounds = aroundPoint((location.value ?? props.center).coordinates)

const point = ([lng, lat]) => ({
  type: "Point",
  coordinates: [Number(lng.toFixed(7)), Number(lat.toFixed(7))],
})

const placeMarker = () => {
  if (!map.value || !location.value) return
  if (!marker) {
    marker = new Marker({
      element: boxMarkerElement({ name: props.name, state: "todo", selected: true }),
      anchor: "center",
      draggable: true,
    })
      .setLngLat(location.value.coordinates)
      .addTo(map.value)
    marker.on("dragend", () => {
      const { lng, lat } = marker.getLngLat()
      accuracy.value = null
      location.value = point([lng, lat])
    })
  } else marker.setLngLat(location.value.coordinates)
}

const onReady = instance => {
  map.value = instance
  instance.on("click", event => {
    accuracy.value = null
    location.value = point([event.lngLat.lng, event.lngLat.lat])
  })
  placeMarker()
}

watch(location, placeMarker)

const locate = () => {
  locating.value = true
  navigator.geolocation.getCurrentPosition(
    position => {
      locating.value = false
      accuracy.value = position.coords.accuracy
      location.value = point([position.coords.longitude, position.coords.latitude])
      map.value?.easeTo({ center: location.value.coordinates, zoom: 17 })
    },
    () => {
      locating.value = false
      message.error(
        "Polohu telefonu se nepodařilo zjistit. Klepni do mapy, kde budka visí.",
      )
    },
    { enableHighAccuracy: true, timeout: 20_000 },
  )
}

if (props.locateOnOpen) locate()

const coordinates = computed(() =>
  location.value
    ? `${location.value.coordinates[1].toFixed(5)}, ${location.value.coordinates[0].toFixed(5)}`
    : "",
)

onBeforeUnmount(() => marker?.remove())
</script>

<template>
  <div class="location-picker">
    <div class="picker-map">
      <BaseMap :bounds="bounds" @ready="onReady">
        <slot />
      </BaseMap>
    </div>
    <div class="row">
      <n-button size="small" :loading="locating" @click="locate">
        <template #icon><AppIcon name="locate" /></template>
        Použít moji polohu
      </n-button>
      <span v-if="location" class="num small muted" data-testid="coordinates">
        {{ coordinates
        }}<template v-if="accuracy"> · ±{{ Math.round(accuracy) }} m</template>
      </span>
      <span v-else class="small muted">Klepni do mapy, kde budka visí.</span>
    </div>
  </div>
</template>

<style scoped>
.location-picker {
  display: grid;
  gap: 10px;
}

.picker-map {
  height: 260px;
  border-radius: var(--r);
  overflow: hidden;
  border: 1px solid var(--line);
}
</style>
