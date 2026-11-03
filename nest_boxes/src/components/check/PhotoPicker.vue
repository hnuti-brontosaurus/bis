<script setup>
import { ref } from "vue"

import AppIcon from "@/components/app/AppIcon.vue"
import { photoDataUri } from "@/composables/files.js"
import { reportError } from "@/data/errors.js"

defineProps({
  // [{ id, order, photo: { small, … } }] already stored with the check
  existing: { type: Array, default: () => [] },
})

// data URIs of photos to upload, in order
const added = defineModel("added", { type: Array, required: true })
// ids of `existing` photos to delete
const removed = defineModel("removed", { type: Array, required: true })

const input = ref(null)
const reading = ref(false)

const onFiles = async event => {
  const files = [...event.target.files]
  event.target.value = ""
  reading.value = true
  try {
    added.value = [...added.value, ...(await Promise.all(files.map(photoDataUri)))]
  } catch (error) {
    reportError(error)
  } finally {
    reading.value = false
  }
}
</script>

<template>
  <div class="photos">
    <template v-for="photo in existing" :key="photo.id">
      <span v-if="!removed.includes(photo.id)" class="photo">
        <img :src="photo.photo.small" alt="Fotka z kontroly" />
        <button
          type="button"
          aria-label="Odebrat fotku"
          @click="removed = [...removed, photo.id]"
        >
          <AppIcon name="x" />
        </button>
      </span>
    </template>
    <span v-for="(photo, index) in added" :key="index" class="photo">
      <img :src="photo" alt="Nová fotka" />
      <button
        type="button"
        aria-label="Odebrat fotku"
        @click="added = added.filter((_, other) => other !== index)"
      >
        <AppIcon name="x" />
      </button>
    </span>
    <button class="add" type="button" :disabled="reading" @click="input.click()">
      <AppIcon name="camera" />
      {{ reading ? "Načítám…" : "Přidat" }}
    </button>
    <input
      ref="input"
      type="file"
      accept="image/*"
      multiple
      hidden
      data-testid="photo-input"
      @change="onFiles"
    />
  </div>
</template>

<style scoped>
.photos {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.photo,
.add {
  width: 76px;
  height: 76px;
  border-radius: var(--r-in);
}

.photo {
  position: relative;
  overflow: hidden;
  background: var(--surface-2);
}

.photo img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.photo button {
  position: absolute;
  top: 4px;
  right: 4px;
  width: 24px;
  height: 24px;
  padding: 0;
  border: 0;
  border-radius: 50%;
  display: grid;
  place-items: center;
  background: var(--surface);
  color: var(--text);
  cursor: pointer;
}

.photo button .icon {
  width: 14px;
  height: 14px;
}

.add {
  border: 1.5px dashed var(--line-strong);
  background: transparent;
  color: var(--muted);
  display: grid;
  place-content: center;
  justify-items: center;
  gap: 2px;
  font: 600 12.5px var(--font);
  cursor: pointer;
}
</style>
