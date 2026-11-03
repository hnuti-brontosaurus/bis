<script setup>
import AppIcon from "@/components/app/AppIcon.vue"
import { isDark, toggleTheme } from "@/composables/theme.js"
</script>

<template>
  <button
    class="icon-button"
    type="button"
    :title="isDark ? 'Světlý režim' : 'Tmavý režim'"
    aria-label="Přepnout světlý a tmavý režim"
    @click="toggleTheme"
  >
    <AppIcon :name="isDark ? 'sun' : 'moon'" />
  </button>
</template>
