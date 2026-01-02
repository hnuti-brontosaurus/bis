<script setup>
import { NTooltip, NBadge, NText } from "naive-ui"
import { useWindowSize } from "@vueuse/core"

const { width } = useWindowSize()

defineProps(["label", "hint", "placement"])
</script>

<template>
  <n-tooltip
    v-if="hint"
    :style="{ maxWidth: `${width / 3}px` }"
    :placement="placement ?? 'top-end'"
  >
    <template #trigger>
      <n-badge :offset="[3, 3]" color="transparent">
        <template #value>
          <n-text depth="3">?</n-text>
        </template>
        <slot />
      </n-badge>
    </template>
    <small>{{ hint }}</small>
  </n-tooltip>
  <template v-else><slot /></template>
</template>
