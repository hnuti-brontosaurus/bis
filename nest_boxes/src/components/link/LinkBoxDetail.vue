<script setup>
import AppIcon from "@/components/app/AppIcon.vue"
import { boxSummary, mapyLink } from "@/composables/boxes.js"
import { formatDate } from "@/composables/czech.js"
import { MATERIAL_LABELS } from "@/composables/labels.js"

defineProps({
  // a row of the link store, see `rows` in data/link.js
  box: { type: Object, required: true },
  typesById: { type: Map, required: true },
})
</script>

<template>
  <div class="box-detail" data-testid="box-detail">
    <p v-if="box.note" class="full-note">
      <b>Poznámka pro dobrovolníky</b>
      {{ box.note }}
    </p>
    <p class="small">
      {{ boxSummary(box, typesById)
      }}<template v-if="box.material"> · {{ MATERIAL_LABELS[box.material] }}</template>
    </p>
    <p v-if="box.installed_on" class="small muted">
      Vyvěšená {{ formatDate(box.installed_on) }}
    </p>
    <a class="small" :href="mapyLink(box.location)" target="_blank" rel="noopener">
      <AppIcon name="map" />Navigovat v Mapy.com
    </a>
  </div>
</template>

<style scoped>
.box-detail {
  display: grid;
  gap: 6px;
  padding: 2px 20px 14px 56px;
  background: var(--primary-soft);
  border-bottom: 1px solid var(--line);
}

.box-detail p {
  margin: 0;
}

.full-note {
  white-space: pre-line;
}

.full-note b {
  display: block;
  font-size: 12px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--muted);
}

.box-detail a {
  justify-self: start;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-weight: 700;
}

.box-detail .icon {
  width: 15px;
  height: 15px;
}

@media (max-width: 720px) {
  .box-detail {
    padding-left: 52px;
    padding-right: 16px;
  }
}
</style>
