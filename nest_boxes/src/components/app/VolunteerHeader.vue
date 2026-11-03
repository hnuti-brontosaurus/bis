<script setup>
import { RouterLink } from "vue-router"

import AppIcon from "@/components/app/AppIcon.vue"
import BrandLogo from "@/components/app/BrandLogo.vue"
import SyncChip from "@/components/app/SyncChip.vue"
import ThemeToggle from "@/components/app/ThemeToggle.vue"

defineProps({
  title: { type: String, required: true },
  subtitle: { type: String, default: "" },
  back: { type: Object, default: null },
  pending: { type: Number, default: 0 },
})
</script>

<template>
  <header class="header">
    <RouterLink v-if="back" class="back" :to="back" aria-label="Zpět">
      <AppIcon name="back" />
    </RouterLink>
    <BrandLogo v-else />
    <div class="title">
      <b>{{ title }}</b>
      <small v-if="subtitle">{{ subtitle }}</small>
    </div>
    <div class="actions">
      <SyncChip :pending="pending" />
      <ThemeToggle />
    </div>
  </header>
</template>

<style scoped>
.header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 16px;
  background: var(--surface);
  color: var(--text);
  border-bottom: 1px solid var(--line);
  position: relative;
  z-index: 3;
  flex: none;
}

.back {
  display: inline-flex;
  color: inherit;
}

.title {
  min-width: 0;
}

.title b {
  display: block;
  font-size: 18px;
  font-weight: 800;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.title small {
  display: block;
  color: var(--muted);
  font-size: 12.5px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.actions {
  margin-left: auto;
  display: flex;
  gap: 8px;
  align-items: center;
}
</style>
