<script setup>
import { APP_PATH } from "@/config.js"

defineProps({ html: { type: String, required: true } })
const emit = defineEmits(["help"])

const HELP_PATH = new RegExp(`^${APP_PATH}/napoveda/([a-z_]+)/?$`)

// A link to another help article opens it where the reader is: in the
// volunteer's offline help, or in the check form's help panel without leaving
// the form. The sanitizer gives every link target="_blank".
const followHelpLink = event => {
  const link = event.target.closest("a")
  if (!link || event.ctrlKey || event.metaKey || event.shiftKey) return
  const url = new URL(link.href)
  const slug = url.origin === location.origin && url.pathname.match(HELP_PATH)?.[1]
  if (!slug) return
  event.preventDefault()
  emit("help", slug)
}
</script>

<template>
  <!-- Sanitized by the API on write (HelpHTMLField) -->
  <!-- eslint-disable-next-line vue/no-v-html -->
  <div class="html-text" @click="followHelpLink" v-html="html" />
</template>
