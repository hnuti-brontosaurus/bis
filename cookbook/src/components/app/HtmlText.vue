<script setup>
defineProps({ html: { type: String, default: "" } })
</script>

<!-- eslint-disable-next-line vue/no-v-html -- sanitized by the backend -->
<template><div class="html-text" v-html="html" /></template>
