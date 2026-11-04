<script setup>
import MarkerGlyph from "@/components/map/MarkerGlyph.vue"
import { SEASON_STATE_LABELS } from "@/composables/labels.js"

// Planned boxes are too rare to explain here
const ENTRIES = ["to_check", "attention", "done"].map(state => ({
  state,
  label: SEASON_STATE_LABELS[state],
}))
</script>

<template>
  <div class="legend">
    <span v-for="entry in ENTRIES" :key="entry.state">
      <MarkerGlyph :state="entry.state" />
      {{ entry.label }}
    </span>
  </div>
</template>

<style scoped>
.legend {
  display: flex;
  flex-wrap: wrap;
  gap: 6px 14px;
  font-size: 13px;
  color: var(--muted);
}

.legend span {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.legend :deep(.marker-glyph) {
  width: 18px;
  height: 18px;
  border-width: 2.5px;
}
</style>
