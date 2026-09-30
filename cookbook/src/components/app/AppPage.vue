<script setup>
import { NButton, NH1 } from "naive-ui"
import { _ } from "@/composables/translations.js"
import { useRender } from "@/contrib/composables/render.js"
import { faChevronLeft } from "@fortawesome/free-solid-svg-icons"
import { useRoute, useRouter } from "vue-router"

const { icon } = useRender()
const route = useRoute()
const router = useRouter()

defineProps(["title"])

// Resolve the back-target from the current route's `meta.back` so that
// e.g. tapping back on a recipe detail returns to the list, not to
// whatever happened to be in browser history (often the edit form we
// just saved). Falls back to history when a route hasn't declared a
// parent.
const onBack = () => {
  const back = route.meta.back
  if (!back) {
    router.back()
    return
  }
  router.push(typeof back === "function" ? back(route) : back)
}
</script>

<template>
  <div class="page">
    <div class="top-row">
      <n-button text class="muted" :render-icon="icon(faChevronLeft)" @click="onBack">{{
        _.common.back
      }}</n-button>
      <div class="page-actions">
        <slot name="actions" />
      </div>
    </div>
    <n-h1 v-if="title" class="title">{{ title }}</n-h1>
    <slot name="extra" />
    <slot />
  </div>
</template>

<style scoped>
.page {
  display: flex;
  flex-direction: column;
  gap: 22px;
}

.top-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
  justify-content: space-between;
}

.page-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
  margin-left: auto;
}

.title {
  margin: 0;
}
</style>
