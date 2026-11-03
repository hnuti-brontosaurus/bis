<script setup>
import { icons } from "@/assets/icons.js"

defineProps({ name: { type: String, required: true } })
</script>

<template>
  <!-- eslint-disable-next-line vue/no-v-html -->
  <svg class="icon" viewBox="0 0 24 24" aria-hidden="true" v-html="icons[name]" />
</template>

<style scoped>
.icon {
  width: 20px;
  height: 20px;
  flex: none;
  stroke: currentColor;
  fill: none;
  stroke-width: 2;
  stroke-linecap: round;
  stroke-linejoin: round;
}
</style>
