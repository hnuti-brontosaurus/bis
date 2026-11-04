<script setup>
import { RouterLink } from "vue-router"
import { NButton } from "naive-ui"

import MarkerGlyph from "@/components/map/MarkerGlyph.vue"

defineProps({
  // [{ key, title, boxes }]
  groups: { type: Array, required: true },
  selectedId: { type: String, default: null },
  // box => { text, tone }, see boxRowDetail in composables/areaBoxes.js
  detail: { type: Function, required: true },
  // box => one of BOX_STATES, see map/markers.js
  stateOf: { type: Function, required: true },
})

const emit = defineEmits(["focus"])
</script>

<template>
  <div class="list" data-testid="box-list">
    <template v-for="group in groups" :key="group.key">
      <div class="group-head">{{ group.title }} · {{ group.boxes.length }}</div>
      <div
        v-for="box in group.boxes"
        :key="box.id"
        class="box-row"
        :class="{ selected: box.id === selectedId }"
        :data-box-row="box.id"
        @click="emit('focus', box)"
      >
        <MarkerGlyph :state="stateOf(box)" />
        <div class="box-text">
          <RouterLink
            class="box-name"
            :to="{ name: 'box', params: { id: box.id } }"
            @click.stop
          >
            {{ box.name }}
          </RouterLink>
          <div class="box-detail">
            <span v-if="detail(box).tone" class="tag" :class="detail(box).tone">
              {{ detail(box).text }}
            </span>
            <template v-else>{{ detail(box).text }}</template>
            <span v-if="!box.is_confirmed" class="tag warn">nepotvrzená</span>
          </div>
        </div>
        <RouterLink
          v-if="box.status !== 'planned'"
          v-slot="{ navigate }"
          :to="{ name: 'check', params: { id: box.id } }"
          custom
        >
          <n-button size="small" secondary @click.stop="navigate"
            >Zkontrolovat</n-button
          >
        </RouterLink>
        <slot name="action" :box="box" :group="group" />
      </div>
    </template>
  </div>
</template>

<style scoped>
.list {
  border-top: 1px solid var(--line);
  padding-bottom: 20px;
}

.group-head {
  position: sticky;
  top: 0;
  z-index: 1;
  padding: 10px 20px 6px;
  background: var(--surface);
  font: 700 12px var(--font);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--muted);
  border-bottom: 1px solid var(--line);
}

.box-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 20px;
  border-bottom: 1px solid var(--line);
  cursor: pointer;
}

.box-row.selected {
  background: var(--primary-soft);
  box-shadow: inset 3px 0 0 var(--accent);
}

.box-text {
  flex: 1;
  min-width: 0;
}

.box-name {
  font-weight: 800;
  color: var(--text);
  text-decoration: none;
}

.box-name:hover {
  text-decoration: underline;
}

.box-detail {
  font-size: 13px;
  color: var(--muted);
  display: flex;
  flex-wrap: wrap;
  gap: 4px 6px;
  align-items: center;
}

@media (max-width: 720px) {
  .box-row,
  .group-head {
    padding-left: 16px;
    padding-right: 16px;
  }
}
</style>
