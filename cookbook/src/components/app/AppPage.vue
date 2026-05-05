<script setup>
import { NButton, NH1, NFlex, NButtonGroup } from "naive-ui"
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
  <n-flex vertical>
    <n-flex justify="space-between" align="start">
      <n-flex :wrap="false" align="baseline">
        <n-button :render-icon="icon(faChevronLeft)" quaternary @click="onBack" />
        <n-h1>{{ title }}</n-h1>
      </n-flex>
      <n-button-group style="margin-left: auto">
        <slot name="actions" />
      </n-button-group>
    </n-flex>
    <n-flex>
      <slot name="extra" />
    </n-flex>
    <slot />
  </n-flex>
</template>

<style scoped></style>
