<script setup>
import AppIcon from "@/components/app/AppIcon.vue"
import { pendingLabel } from "@/composables/czech.js"

defineProps({ pending: { type: Number, required: true } })
</script>

<template>
  <span v-if="pending" class="sync">
    <AppIcon name="cloud" />
    <span>{{ pendingLabel(pending) }}</span>
  </span>
</template>

<style scoped>
.sync {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 700;
  padding: 6px 10px;
  border-radius: var(--r-chip);
  background: var(--warn-soft);
  color: var(--warn);
  white-space: nowrap;
}
</style>
