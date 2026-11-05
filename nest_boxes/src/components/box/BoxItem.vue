<script setup>
import { computed } from "vue"
import { RouterLink } from "vue-router"

import AppIcon from "@/components/app/AppIcon.vue"
import MarkerGlyph from "@/components/map/MarkerGlyph.vue"
import { boxTags, mapyLink, typeName } from "@/composables/boxes.js"

const props = defineProps({
  box: { type: Object, required: true },
  // one of BOX_STATES, see map/markers.js
  state: { type: String, required: true },
  expanded: { type: Boolean, default: false },
  typesById: { type: Map, required: true },
  // where the name leads; a plain name without it
  to: { type: Object, default: null },
  // muted text after the tags, such as how far the box is
  aside: { type: String, default: "" },
})

const emit = defineEmits(["toggle"])

const tags = computed(() => boxTags(props.box))
</script>

<template>
  <div class="box-item" :class="{ expanded }" :data-box-row="box.id">
    <div class="head" @click="emit('toggle')">
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
      <p class="type-line">
        {{ typeName(typesById, box.type_id) }} ·
        <a
          :href="mapyLink(box.location)"
          target="_blank"
          rel="noopener"
          :aria-label="`Budka ${box.name} na Mapy.com`"
          @click.stop
          ><AppIcon name="map" />Mapy.com</a
        >
      </p>
      <slot name="extra" />
    </div>
  </div>
</template>

<style scoped>
.box-item {
  border-bottom: 1px solid var(--line);
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

.detail {
  display: grid;
  gap: 6px;
  padding: 0 20px 12px 56px;
  font-size: 14px;
}

.detail :deep(p) {
  margin: 0;
}

.full-note {
  white-space: pre-line;
}

.type-line {
  color: var(--muted);
}

.type-line a {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  font-weight: 700;
}

.type-line .icon {
  width: 15px;
  height: 15px;
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
