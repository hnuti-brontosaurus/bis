<script setup>
defineProps({ html: { type: String, required: true } })
</script>

<template>
  <!-- Sanitized by the API on write (ArticleHTMLField) -->
  <!-- eslint-disable-next-line vue/no-v-html -->
  <div class="html-text" v-html="html" />
</template>
