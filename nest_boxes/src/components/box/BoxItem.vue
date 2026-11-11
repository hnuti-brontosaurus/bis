<script setup>
import { computed } from "vue"
import { RouterLink } from "vue-router"
import { NButton } from "naive-ui"

import AppIcon from "@/components/app/AppIcon.vue"
import MarkerGlyph from "@/components/map/MarkerGlyph.vue"
import { boxTags, mapyLink, typeName } from "@/composables/boxes.js"

const props = defineProps({
  box: { type: Object, required: true },
  // one of BOX_STATES, see map/markers.js
  state: { type: String, required: true },
  expanded: { type: Boolean, default: false },
  // one of the boxes picked with Shift
  picked: { type: Boolean, default: false },
  typesById: { type: Map, required: true },
  // where the name leads; a plain name without it
  to: { type: Object, default: null },
  // muted text after the tags, such as how far the box is
  aside: { type: String, default: "" },
  // the lines an opened row lists under the type
  facts: { type: Array, default: () => [] },
})

// the click, to tell a Shift click
const emit = defineEmits(["toggle"])

const tags = computed(() => boxTags(props.box))
const allFacts = computed(() => {
  const type = typeName(props.typesById, props.box.type_id)
  return [type.charAt(0).toUpperCase() + type.slice(1), ...props.facts]
})
</script>

<template>
  <div class="box-item" :class="{ expanded, picked }" :data-box-row="box.id">
    <!-- Shift + click would select the text of the rows in between -->
    <div
      class="head"
      @mousedown="event => event.shiftKey && event.preventDefault()"
      @click="emit('toggle', $event)"
    >
      <MarkerGlyph :state="state" />
      <div class="text">
        <div class="title">
          <RouterLink v-if="to" class="name" :to="to" @click.stop>
            {{ box.name || "Nová budka" }}
          </RouterLink>
          <span v-else class="name">{{ box.name || "Nová budka" }}</span>
          <span v-for="tag in tags" :key="tag.text" class="tag" :class="tag.tone">
            {{ tag.text }}
          </span>
          <slot name="tags" />
          <span v-if="aside" class="aside">{{ aside }}</span>
        </div>
        <div v-if="box.note && !expanded" class="note-line">{{ box.note }}</div>
      </div>
      <slot name="action" />
    </div>
    <div v-if="expanded" class="detail" data-testid="box-detail">
      <p v-if="box.note" class="full-note">{{ box.note }}</p>
      <ul class="box-facts">
        <li v-for="fact in allFacts" :key="fact">{{ fact }}</li>
      </ul>
      <div class="actions">
        <n-button
          tag="a"
          size="small"
          secondary
          :href="mapyLink(box.location)"
          target="_blank"
          rel="noopener"
          :aria-label="`Budka ${box.name} na Mapy.com`"
          @click.stop
        >
          <template #icon><AppIcon name="map" /></template>
          Mapy.com
        </n-button>
        <slot name="actions" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.box-item {
  border-bottom: 1px solid var(--line);
}

.box-item.picked {
  background: var(--primary-soft);
}

.box-item.expanded {
  background: var(--primary-soft);
  box-shadow: inset 3px 0 0 var(--accent);
}

.head {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 20px;
  cursor: pointer;
}

.text {
  flex: 1;
  min-width: 0;
}

.title {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 4px 8px;
}

.name {
  font-weight: 800;
  color: var(--text);
  text-decoration: none;
}

a.name:hover {
  text-decoration: underline;
}

.aside {
  font-size: 13px;
  color: var(--muted);
}

.note-line {
  margin-top: 2px;
  font-size: 13px;
  color: var(--muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* The facts on the left, the buttons on the right under the row's own button */
.detail {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  gap: 8px 16px;
  padding: 0 20px 14px 56px;
  font-size: 14px;
}

.full-note {
  flex-basis: 100%;
  margin: 0;
  white-space: pre-line;
}

.box-facts {
  flex: 1 1 120px;
  display: grid;
  gap: 2px;
  margin: 0;
  padding: 0;
  list-style: none;
  color: var(--muted);
}

.box-facts li:first-child {
  color: var(--text);
  font-weight: 700;
}

/* As far apart as the row's own button is from the first of them */
.actions {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 10px;
  margin-left: auto;
}

@media (max-width: 720px) {
  .head {
    padding-left: 16px;
    padding-right: 16px;
  }

  .detail {
    padding-left: 52px;
    padding-right: 16px;
  }
}
</style>
