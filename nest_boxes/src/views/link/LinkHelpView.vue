<script setup>
import { computed } from "vue"
import { RouterLink, useRoute } from "vue-router"

import HtmlText from "@/components/app/HtmlText.vue"
import VolunteerHeader from "@/components/app/VolunteerHeader.vue"
import { helpTitle } from "@/composables/labels.js"
import { useLinkStore } from "@/data/link.js"

const route = useRoute()
const link = useLinkStore()

const articles = computed(() => link.payload.help_articles)
const article = computed(
  () =>
    articles.value.find(item => item.slug === route.params.slug) ?? articles.value[0],
)
</script>

<template>
  <VolunteerHeader
    title="Nápověda"
    :subtitle="link.payload.area.name"
    :back="{ name: 'link' }"
    :pending="link.pending"
  />
  <main class="page help">
    <nav class="toc">
      <RouterLink
        v-for="item in articles"
        :key="item.slug"
        :to="{ name: 'link_help', params: { slug: item.slug } }"
        :class="{ active: item.slug === article.slug }"
      >
        {{ helpTitle(item) }}
      </RouterLink>
    </nav>
    <article class="stack">
      <h1>{{ helpTitle(article) }}</h1>
      <HtmlText v-if="article.content" :html="article.content" />
      <p v-else class="muted">Tahle nápověda se teprve píše.</p>
    </article>
  </main>
</template>

<style scoped>
.help {
  grid-template-columns: 240px minmax(0, 1fr);
  align-items: start;
}

.toc {
  display: grid;
  gap: 2px;
}

.toc a {
  padding: 8px 12px;
  border-radius: var(--r-in);
  color: var(--text);
  text-decoration: none;
  font-weight: 600;
}

.toc a.active {
  background: var(--primary-soft);
  color: var(--primary-text);
}

@media (max-width: 720px) {
  .help {
    grid-template-columns: minmax(0, 1fr);
  }

  .toc {
    display: flex;
    gap: 6px;
    overflow-x: auto;
    padding-bottom: 4px;
  }

  .toc a {
    white-space: nowrap;
    border: 1px solid var(--line);
  }
}
</style>
