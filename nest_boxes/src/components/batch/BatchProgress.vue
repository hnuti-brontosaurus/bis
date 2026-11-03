<script setup>
import { computed } from "vue"

import { daysBetween, dayCountLabel, pendingLabel } from "@/composables/czech.js"

const REMINDED_AFTER_DAYS = 7

const props = defineProps({
  // batches/ shape
  batch: { type: Object, required: true },
})

const age = computed(() => daysBetween(props.batch.created_at))
const share = computed(() =>
  props.batch.box_count ? (props.batch.checked_count / props.batch.box_count) * 100 : 0,
)
</script>

<template>
  <div class="batch-progress">
    <div class="row small">
      <span class="num">
        <b>{{ batch.checked_count }} z {{ batch.box_count }}</b> zkontrolováno
      </span>
      <span v-if="batch.pending_count" class="muted">
        · {{ pendingLabel(batch.pending_count) }} na potvrzení
      </span>
      <span v-if="batch.closed_at" class="tag age">uzavřená</span>
      <span v-else class="tag age" :class="{ warn: age > REMINDED_AFTER_DAYS }">
        otevřená {{ age ? dayCountLabel(age) : "dnes" }}
      </span>
    </div>
    <div class="prog thin"><i :style="{ width: `${share}%` }" /></div>
  </div>
</template>

<style scoped>
.batch-progress {
  display: grid;
  gap: 8px;
}

.age {
  margin-left: auto;
}
</style>
