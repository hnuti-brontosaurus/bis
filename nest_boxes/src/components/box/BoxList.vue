<script setup>
import { computed, ref, watch } from "vue"
import { RouterLink } from "vue-router"
import { NButton } from "naive-ui"
import { useElementVisibility } from "@vueuse/core"

import MarkerGlyph from "@/components/map/MarkerGlyph.vue"

// Rows rendered at once; a whole region's boxes would take seconds
const PAGE = 20

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

const limit = ref(PAGE)
const more = ref(null)
const moreVisible = useElementVisibility(more)

const total = computed(() =>
  props.groups.reduce((sum, group) => sum + group.boxes.length, 0),
)
const shownGroups = computed(() => {
  let left = limit.value
  return props.groups
    .map(group => {
      const shown = group.boxes.slice(0, Math.max(left, 0))
      left -= shown.length
      return { ...group, shown }
    })
    .filter(group => group.shown.length)
})

const showMore = () => (limit.value += PAGE)

// Infinite scroll: more rows while the button is in sight, one page per render
watch(
  [moreVisible, limit],
  () => moreVisible.value && limit.value < total.value && showMore(),
  { flush: "post" },
)

// A row picked on the map has to be there to scroll to
watch([() => props.selectedId, () => props.groups], ([selected, groups]) => {
  const order = groups.flatMap(group => group.boxes.map(box => box.id))
  const index = order.indexOf(selected)
  if (index >= limit.value) limit.value = Math.ceil((index + 1) / PAGE) * PAGE
})
</script>

<template>
  <div class="list" data-testid="box-list">
    <template v-for="group in shownGroups" :key="group.key">
      <div class="group-head">{{ group.title }} · {{ group.boxes.length }}</div>
      <div
        v-for="box in group.shown"
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
    <div v-if="limit < total" class="more">
      <n-button ref="more" size="small" quaternary @click="showMore">
        Zobrazit další ({{ total - limit }})
      </n-button>
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

.more {
  display: grid;
  justify-items: center;
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
