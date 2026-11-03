<script setup>
import { RouterLink } from "vue-router"

import AppIcon from "@/components/app/AppIcon.vue"
import HtmlText from "@/components/app/HtmlText.vue"
import { helpTitle } from "@/composables/labels.js"

defineProps({
  // { slug, title, content }
  article: { type: Object, required: true },
  // Off for the volunteer's offline pages, where the help page isn't cached
  linked: { type: Boolean, default: true },
})
</script>

<template>
  <div class="help-panel" data-testid="help-panel">
    <p class="eyebrow">Nápověda</p>
    <h3>{{ helpTitle(article) }}</h3>
    <HtmlText v-if="article.content" class="small" :html="article.content" />
    <p v-else class="small muted">Tahle nápověda se teprve píše.</p>
    <RouterLink
      v-if="linked"
      class="small more"
      :to="{ name: 'help_article', params: { slug: article.slug } }"
    >
      Celý návod
      <AppIcon name="chev" />
    </RouterLink>
  </div>
</template>

<style scoped>
.help-panel {
  display: grid;
  gap: 10px;
  align-content: start;
}

.more {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  font-weight: 700;
}

.more .icon {
  width: 16px;
  height: 16px;
}
</style>
