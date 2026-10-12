<script setup>
import { NImage } from "naive-ui"

defineProps({ photo: { type: Object, required: true }, alt: String })
</script>

<template>
  <n-image
    class="recipe-photo"
    :src="photo.medium"
    :preview-src="photo.large"
    :alt="alt"
  />
</template>

<style scoped>
.recipe-photo {
  display: flex;
  width: fit-content;
  overflow: hidden;
  border: 1px solid var(--line);
  border-radius: 4px;
  cursor: zoom-in;
}

.recipe-photo :deep(img) {
  display: block;
  max-width: 100%;
  max-height: 280px;
  object-fit: contain;
}
</style>
