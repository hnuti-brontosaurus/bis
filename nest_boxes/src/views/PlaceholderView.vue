<script setup>
import { useRoute } from "vue-router"

import VolunteerHeader from "@/components/app/VolunteerHeader.vue"

defineProps({ title: { type: String, required: true } })

const route = useRoute()
</script>

<template>
  <VolunteerHeader v-if="route.meta.volunteer" :title="title" />
  <main class="page">
    <h1>{{ title }}</h1>
    <p class="muted">Tahle stránka se teprve staví.</p>
  </main>
</template>
