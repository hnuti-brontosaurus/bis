<script setup>
import { NImage, NImageGroup } from "naive-ui"

defineProps({ photos: { type: Array, required: true }, alt: String })
</script>

<template>
  <div class="recipe-photos" :class="{ single: photos.length === 1 }">
    <n-image-group>
      <n-image
        v-for="{ id, photo } in photos"
        :key="id"
        class="recipe-photo"
        :src="photo.medium"
        :preview-src="photo.large"
        :alt="alt"
      />
    </n-image-group>
  </div>
</template>

<style scoped>
.recipe-photos {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

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
  max-height: 160px;
  object-fit: contain;
}

.single .recipe-photo :deep(img) {
  max-height: 280px;
}
</style>
