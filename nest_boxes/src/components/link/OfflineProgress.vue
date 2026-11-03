<script setup>
import { computed } from "vue"

import MarkerGlyph from "@/components/map/MarkerGlyph.vue"
import { boxCountLabel } from "@/composables/czech.js"
import { useLinkStore } from "@/data/link.js"

const link = useLinkStore()

const share = computed(() =>
  link.prefetch.total ? (link.prefetch.done / link.prefetch.total) * 100 : 0,
)
</script>

<template>
  <section class="offline stack" data-testid="offline-progress">
    <h3>Stahuji oblast do telefonu</h3>
    <div class="row">
      <MarkerGlyph state="done" />
      <span>{{ boxCountLabel(link.payload.boxes.length) }} a jejich údaje</span>
    </div>
    <div class="row">
      <MarkerGlyph state="done" />
      <span>Nápověda k čištění a obyvatelům</span>
    </div>
    <div class="row">
      <MarkerGlyph :state="link.prefetch.state === 'running' ? 'to_check' : 'done'" />
      <span class="spacer">Mapa oblasti</span>
      <span v-if="link.prefetch.state === 'partial'" class="small warn-text">
        stažená jen zčásti
      </span>
      <span v-else-if="link.prefetch.total" class="num muted small">
        {{ link.prefetch.done }} / {{ link.prefetch.total }} dlaždic
      </span>
    </div>
    <div class="prog thin"><i :style="{ width: `${share}%` }" /></div>
    <p class="small muted">Pak to půjde i bez signálu. V lese ho často nebývá.</p>
  </section>
</template>

<style scoped>
.offline {
  gap: 12px;
}

.warn-text {
  color: var(--warn);
  font-weight: 700;
}
</style>
