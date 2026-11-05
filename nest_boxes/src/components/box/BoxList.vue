<script setup>
import { computed, ref, watch } from "vue"
import { RouterLink } from "vue-router"
import { NButton, NPagination } from "naive-ui"

import MarkerGlyph from "@/components/map/MarkerGlyph.vue"

// Rows rendered at once; a whole region's boxes would take seconds
const PAGE_SIZE = 50

const props = defineProps({
  // [{ key, title, boxes }]
  groups: { type: Array, required: true },
  selectedId: { type: String, default: null },
  // box => { text, tone }, see boxRowDetail in composables/areaBoxes.js
  detail: { type: Function, required: true },
  // box => one of BOX_STATES, see map/markers.js
  stateOf: { type: Function, required: true },
})

const emit = defineEmits(["focus"])

const list = ref(null)
const page = ref(1)

const order = computed(() =>
  props.groups.flatMap(group => group.boxes.map(box => box.id)),
)
const total = computed(() => order.value.length)
const pageCount = computed(() => Math.max(1, Math.ceil(total.value / PAGE_SIZE)))

const pageGroups = computed(() => {
  let skip = (page.value - 1) * PAGE_SIZE
  let left = PAGE_SIZE
  const shown = []
  for (const group of props.groups) {
    const boxes = group.boxes.slice(skip, skip + left)
    skip = Math.max(0, skip - group.boxes.length)
    if (!boxes.length) continue
    left -= boxes.length
    shown.push({
      ...group,
      rows: boxes.map(box => ({
        box,
        detail: props.detail(box),
        state: props.stateOf(box),
      })),
    })
    if (!left) break
  }
  return shown
})

const firstShown = computed(() => (page.value - 1) * PAGE_SIZE + 1)
const lastShown = computed(() => Math.min(page.value * PAGE_SIZE, total.value))

// A row picked on the map has to be on the page to scroll to
watch([() => props.selectedId, order], ([selected]) => {
  const index = order.value.indexOf(selected)
  if (index >= 0) page.value = Math.floor(index / PAGE_SIZE) + 1
  else page.value = Math.min(page.value, pageCount.value)
})

const turnPage = value => {
  page.value = value
  list.value.scrollIntoView({ block: "start" })
}
</script>

<template>
  <div ref="list" class="list" data-testid="box-list">
    <template v-for="group in pageGroups" :key="group.key">
      <div class="group-head">{{ group.title }} · {{ group.boxes.length }}</div>
      <div
        v-for="{ box, detail: boxDetail, state } in group.rows"
        :key="box.id"
        class="box-row"
        :class="{ selected: box.id === selectedId }"
        :data-box-row="box.id"
        @click="emit('focus', box)"
      >
        <MarkerGlyph :state="state" />
        <div class="box-text">
          <RouterLink
            class="box-name"
            :to="{ name: 'box', params: { id: box.id } }"
            @click.stop
          >
            {{ box.name }}
          </RouterLink>
          <div class="box-detail">
            <span v-if="boxDetail.tone" class="tag" :class="boxDetail.tone">
              {{ boxDetail.text }}
            </span>
            <template v-else>{{ boxDetail.text }}</template>
            <span v-if="box.is_new" class="tag warn">nová</span>
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
    <div v-if="pageCount > 1" class="pager">
      <span class="small muted num"
        >{{ firstShown }}–{{ lastShown }} z {{ total }}</span
      >
      <n-pagination
        :page="page"
        :page-count="pageCount"
        :page-slot="5"
        size="small"
        @update:page="turnPage"
      />
    </div>
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

.pager {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 8px 12px;
  padding: 12px 20px;
}

@media (max-width: 720px) {
  .box-row,
  .group-head {
    padding-left: 16px;
    padding-right: 16px;
  }
}
</style>
