<script setup>
import { computed, ref, watch } from "vue"
import { RouterLink } from "vue-router"
import { NButton, NPagination } from "naive-ui"

import AppIcon from "@/components/app/AppIcon.vue"
import BoxItem from "@/components/box/BoxItem.vue"
import MoveBoxDialog from "@/components/box/MoveBoxDialog.vue"

// Rows rendered at once; a whole region's boxes would take seconds
const PAGE_SIZE = 50

const props = defineProps({
  // [{ key, title, boxes }]
  groups: { type: Array, required: true },
  selectedId: { type: String, default: null },
  // the boxes picked with Shift, or null where a Shift click is just a click
  pickedIds: { type: Array, default: null },
  // box => [line], what an opened row adds, see boxFacts in composables/areaBoxes.js
  facts: { type: Function, required: true },
  typesById: { type: Map, required: true },
  // box => one of BOX_STATES, see map/markers.js
  stateOf: { type: Function, required: true },
})

// "moved" carries the boxes as saved in their new area
const emit = defineEmits(["focus", "pick", "moved"])

const list = ref(null)
const moving = ref(null)
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
      <BoxItem
        v-for="{ box, state } in group.rows"
        :key="box.id"
        :box="box"
        :state="state"
        :expanded="box.id === selectedId"
        :picked="Boolean(pickedIds?.includes(box.id))"
        :types-by-id="typesById"
        :facts="facts(box)"
        :to="{ name: 'box', params: { id: box.id } }"
        @toggle="event => emit(pickedIds && event.shiftKey ? 'pick' : 'focus', box)"
      >
        <template #tags>
          <span v-if="box.is_new" class="tag warn">nová</span>
        </template>
        <template #action>
          <RouterLink
            v-if="box.status !== 'planned' && box.status !== 'ended'"
            v-slot="{ navigate }"
            :to="{ name: 'check', params: { id: box.id } }"
            custom
          >
            <n-button size="small" secondary @click.stop="navigate"
              >Zkontrolovat</n-button
            >
          </RouterLink>
        </template>
        <template #actions>
          <n-button
            v-if="box.status !== 'ended'"
            size="small"
            secondary
            @click.stop="moving = box"
          >
            <template #icon><AppIcon name="layers" /></template>
            Přesunout
          </n-button>
        </template>
      </BoxItem>
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
    <MoveBoxDialog
      v-if="moving"
      :boxes="[moving]"
      @close="moving = null"
      @moved="emit('moved', $event)"
    />
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

.pager {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 8px 12px;
  padding: 12px 20px;
}

@media (max-width: 720px) {
  .group-head {
    padding-left: 16px;
    padding-right: 16px;
  }
}
</style>
