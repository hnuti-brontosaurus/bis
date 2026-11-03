<script setup>
import { computed } from "vue"

import { glyphMarkup } from "@/components/map/markers.js"

const props = defineProps({
  // one of BOX_STATES, or "planned"
  state: { type: String, required: true },
})

const markup = computed(() => glyphMarkup(props.state))
</script>

<template>
  <!-- eslint-disable-next-line vue/no-v-html -->
  <span class="marker-glyph" :class="state" v-html="markup" />
</template>
