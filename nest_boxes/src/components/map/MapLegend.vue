<script setup>
import MarkerGlyph from "@/components/map/MarkerGlyph.vue"

const ENTRIES = [
  { state: "todo", label: "Ke kontrole" },
  { state: "done", label: "Hotovo" },
  { state: "not_found", label: "Nenalezena" },
  { state: "planned", label: "Plánovaná" },
]
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
