<script setup>
import { NTooltip, NBadge, NText } from "naive-ui"
import { useWindowSize } from "@vueuse/core"

const { width } = useWindowSize()

defineProps(["label", "hint", "placement"])
</script>

<template>
  <n-tooltip v-if="hint" :width="width / 3" :placement="placement ?? 'top-end'">
    <template #trigger>
      <n-badge :offset="[5, 2]" color="transparent" style="font-family: unset">
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
