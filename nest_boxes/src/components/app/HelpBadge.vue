<script setup>
defineEmits(["open"])
</script>

<template>
  <button class="help-badge" type="button" title="Nápověda" @click="$emit('open')">
    ?
  </button>
</template>

<style scoped>
.help-badge {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  border: 1.5px solid var(--accent);
  background: var(--accent-soft);
  color: var(--accent);
  display: inline-grid;
  place-items: center;
  font: 800 12.5px var(--font);
  cursor: pointer;
  padding: 0;
  vertical-align: middle;
}
</style>
