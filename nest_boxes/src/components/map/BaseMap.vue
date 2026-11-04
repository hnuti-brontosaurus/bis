<script setup>
import {
  computed,
  onBeforeUnmount,
  onMounted,
  provide,
  reactive,
  ref,
  shallowRef,
  watch,
} from "vue"
import { Map as MaplibreMap, NavigationControl } from "maplibre-gl"

import { styleFor } from "@/components/map/mapStyle.js"
import { terrainSources } from "@/components/map/terrain.js"
import "@/components/map/maplibre.js"
import { loadBaseStyle } from "@/components/map/baseStyle.js"
import { CZECHIA_BOUNDS, MAP_ATTRIBUTION } from "@/config.js"
import { palette } from "@/composables/theme.js"

const props = defineProps({
  bounds: { type: Array, default: () => CZECHIA_BOUNDS },
  interactive: { type: Boolean, default: true },
  // the part of the map hidden under a bottom sheet, kept out of fitBounds
  bottomInset: { type: Number, default: 0 },
})

const emit = defineEmits(["ready"])

const container = ref(null)
const map = shallowRef(null)
const baseStyle = shallowRef(null)
const overlays = reactive(new Map())

// Overlays are part of the style, so a theme switch (setStyle) keeps them
// and recolours them along with the base layers.
const style = computed(() => {
  if (!baseStyle.value) return null
  const full = styleFor(baseStyle.value, palette.value, terrainSources())
  for (const build of overlays.values()) {
    const overlay = build(palette.value)
    full.sources = { ...full.sources, ...overlay.sources }
    full.layers = [...full.layers, ...overlay.layers]
  }
  return full
})

provide("map", {
  map,
  setOverlay: (id, build) => overlays.set(id, build),
  removeOverlay: id => overlays.delete(id),
})

let resizeObserver = null
let stopStyleWatch = null
let stopInsetWatch = null

onMounted(async () => {
  baseStyle.value = await loadBaseStyle()
  map.value = new MaplibreMap({
    container: container.value,
    style: style.value,
    bounds: props.bounds,
    fitBoundsOptions: {
      padding: { top: 24, left: 24, right: 24, bottom: 24 + props.bottomInset },
    },
    interactive: props.interactive,
    attributionControl: { customAttribution: MAP_ATTRIBUTION },
    dragRotate: false,
    pitchWithRotate: false,
  })
  map.value.touchZoomRotate.disableRotation()
  if (props.interactive)
    map.value.addControl(new NavigationControl({ showCompass: false }))
  resizeObserver = new ResizeObserver(() => map.value.resize())
  resizeObserver.observe(container.value)
  // Camera moves work before "load", which waits for slow tiles too
  emit("ready", map.value)
  stopStyleWatch = watch(style, value => map.value.setStyle(value))
  stopInsetWatch = watch(
    () => props.bottomInset,
    inset => map.value.easeTo({ padding: { bottom: inset } }),
  )
})

onBeforeUnmount(() => {
  stopStyleWatch?.()
  stopInsetWatch?.()
  resizeObserver?.disconnect()
  map.value?.remove()
})
</script>

<template>
  <div ref="container" class="map" data-testid="map">
    <slot v-if="map" />
  </div>
</template>

<style scoped>
.map {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 0;
  background: var(--map-out);
}
</style>
