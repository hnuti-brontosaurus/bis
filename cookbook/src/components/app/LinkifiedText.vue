<script setup>
import { computed } from "vue"

const props = defineProps({
  text: { type: String, default: "" },
})

const URL_RE = /(https?:\/\/[^\s<]+[^\s<.,:;"')\]])/g

const segments = computed(() => {
  const out = []
  let last = 0
  for (const m of props.text.matchAll(URL_RE)) {
    if (m.index > last) {
      out.push({ type: "text", value: props.text.slice(last, m.index) })
    }
    out.push({ type: "url", value: m[0] })
    last = m.index + m[0].length
  }
  if (last < props.text.length) {
    out.push({ type: "text", value: props.text.slice(last) })
  }
  return out
})
</script>

<template>
  <template v-for="(seg, i) in segments" :key="i">
    <a
      v-if="seg.type === 'url'"
      :href="seg.value"
      target="_blank"
      rel="noopener noreferrer"
      >{{ seg.value }}</a
    >
    <template v-else>{{ seg.value }}</template>
  </template>
</template>
