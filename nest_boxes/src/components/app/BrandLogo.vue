<script setup>
import { BRONTIK_PATH, BRONTIK_VIEW_BOX } from "@/assets/brontik.js"
</script>

<template>
  <svg class="logo" :viewBox="BRONTIK_VIEW_BOX" aria-hidden="true">
    <path :d="BRONTIK_PATH" />
  </svg>
</template>

<style scoped>
.logo {
  width: 30px;
  height: 36px;
  flex: none;
  fill: var(--logo);
}
</style>
