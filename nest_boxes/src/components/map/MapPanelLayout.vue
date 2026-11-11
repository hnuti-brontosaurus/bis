<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from "vue"
import { useMediaQuery } from "@vueuse/core"

import {
  clampHeight,
  nearestStop,
  nextStopOnTap,
  sheetHeights,
} from "@/components/map/sheet.js"

// The handle with its margins, and the sheet's top border
const HANDLE_HEIGHT = 22
const TAP_DISTANCE = 6

const layout = ref(null)
const summary = ref(null)
const containerHeight = ref(0)
const summaryHeight = ref(0)
const stop = ref("half")
const dragHeight = ref(null)

const heights = computed(() =>
  sheetHeights(containerHeight.value, HANDLE_HEIGHT + summaryHeight.value),
)
const sheetHeight = computed(() => dragHeight.value ?? heights.value[stop.value])
const isPhone = useMediaQuery("(max-width: 720px)")
const bottomInset = computed(() => (isPhone.value ? heights.value[stop.value] : 0))
// Where the phone's sheet rests; null on a desktop, which has no sheet
const sheetStop = computed(() => (isPhone.value ? stop.value : null))

let drag = null

// The capture would retarget the click of a button in the summary to the zone
const onPointerDown = event => {
  if (event.target.closest("button, a, input")) return
  drag = { startY: event.clientY, startHeight: sheetHeight.value, moved: false }
  event.currentTarget.setPointerCapture(event.pointerId)
}

const onPointerMove = event => {
  if (!drag) return
  const delta = drag.startY - event.clientY
  drag.moved ||= Math.abs(delta) > TAP_DISTANCE
  if (drag.moved)
    dragHeight.value = clampHeight(heights.value, drag.startHeight + delta)
}

const onPointerUp = () => {
  if (!drag) return
  stop.value = drag.moved
    ? nearestStop(heights.value, dragHeight.value)
    : nextStopOnTap(stop.value)
  dragHeight.value = null
  drag = null
}

const resizeObserver = new ResizeObserver(() => {
  containerHeight.value = layout.value.clientHeight
  // Rounded down, a fraction of a pixel would overflow the page into a scrollbar
  summaryHeight.value = Math.ceil(summary.value.getBoundingClientRect().height)
})

onMounted(() => {
  resizeObserver.observe(layout.value)
  resizeObserver.observe(summary.value)
})

onBeforeUnmount(() => resizeObserver.disconnect())
</script>

<template>
  <div ref="layout" class="map-panel" :class="{ dragging: dragHeight !== null }">
    <div class="map-area">
      <slot name="map" :bottom-inset="bottomInset" :sheet-stop="sheetStop" />
    </div>
    <aside
      class="panel"
      :style="{ '--sheet-height': `${sheetHeight}px` }"
      data-testid="panel"
    >
      <div
        class="drag-zone"
        @pointerdown="onPointerDown"
        @pointermove="onPointerMove"
        @pointerup="onPointerUp"
        @pointercancel="onPointerUp"
      >
        <div class="handle" />
        <div ref="summary">
          <slot name="summary" />
        </div>
      </div>
      <div class="panel-body">
        <slot />
      </div>
    </aside>
  </div>
</template>

<style scoped>
.map-panel {
  flex: 1;
  min-height: 0;
  display: grid;
  grid-template-columns: minmax(0, 1fr) 440px;
  position: relative;
}

/* A Shift + click picks boxes; it must not select the markers' text */
.map-area {
  min-height: 0;
  position: relative;
  user-select: none;
}

.panel {
  background: var(--surface);
  border-left: 1px solid var(--line);
  display: flex;
  flex-direction: column;
  min-height: 0;
  z-index: 2;
}

.drag-zone {
  flex: none;
}

.handle {
  display: none;
}

.panel-body {
  flex: 1;
  min-height: 0;
  overflow: auto;
}

@media (max-width: 720px) {
  .map-panel {
    display: block;
  }

  .map-area {
    position: absolute;
    inset: 0;
  }

  .panel {
    position: absolute;
    left: 0;
    right: 0;
    bottom: 0;
    height: var(--sheet-height);
    border-left: 0;
    border-top: 1px solid var(--line);
    border-radius: 20px 20px 0 0;
    box-shadow: 0 -6px 28px var(--shadow-c);
    transition: height 0.2s ease;
  }

  .dragging .panel {
    transition: none;
  }

  .drag-zone {
    touch-action: none;
    cursor: grab;
  }

  .handle {
    display: block;
    width: 44px;
    height: 5px;
    border-radius: 9px;
    background: var(--line-strong);
    margin: 8px auto;
  }
}

@media (prefers-reduced-motion: reduce) {
  .panel {
    transition: none;
  }
}
</style>
