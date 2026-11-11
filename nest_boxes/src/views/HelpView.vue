<script setup>
import { computed, ref, watch } from "vue"
import { RouterLink, useRoute, useRouter } from "vue-router"
import { NButton, NInput, useMessage } from "naive-ui"

import AppIcon from "@/components/app/AppIcon.vue"
import HtmlEditor from "@/components/app/HtmlEditor.vue"
import HtmlText from "@/components/app/HtmlText.vue"
import { HELP_TITLES, helpTitle } from "@/composables/labels.js"
import { useLoad } from "@/composables/useLoad.js"
import { useAuthStore } from "@/data/auth.js"
import { reportError } from "@/data/errors.js"
import { listHelpArticles, updateHelpArticle, uploadHelpImage } from "@/data/manage.js"

const FIRST_ARTICLE = "cleaning_howto"
const ORDER = Object.keys(HELP_TITLES)

const route = useRoute()
const router = useRouter()
const message = useMessage()
const auth = useAuthStore()

const { data: articles, reload } = useLoad(async () =>
  (await listHelpArticles()).sort(
    (a, b) => ORDER.indexOf(a.slug) - ORDER.indexOf(b.slug),
  ),
)

const slug = computed(() => route.params.slug ?? FIRST_ARTICLE)
const article = computed(() => articles.value?.find(item => item.slug === slug.value))

const editing = ref(false)
const draft = ref({ title: "", content: "" })
const saving = ref(false)

watch(slug, () => (editing.value = false))

const edit = () => {
  draft.value = { title: helpTitle(article.value), content: article.value.content }
  editing.value = true
}

const uploadImage = async dataUri => (await uploadHelpImage(slug.value, dataUri)).src

const save = async () => {
  saving.value = true
  try {
    await updateHelpArticle(slug.value, draft.value)
    await reload()
    editing.value = false
    message.success("Nápověda je uložená.")
  } catch (error) {
    reportError(error)
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <main class="page help-page">
    <div v-if="articles" class="article-layout">
      <nav class="toc" aria-label="Nápověda">
        <p class="eyebrow">Nápověda</p>
        <RouterLink
          v-for="item in articles"
          :key="item.slug"
          :to="{ name: 'help_article', params: { slug: item.slug } }"
          :class="{ on: item.slug === slug }"
        >
          {{ helpTitle(item) }}
        </RouterLink>
      </nav>
      <article v-if="article" class="prose">
        <template v-if="editing">
          <div class="field">
            <label for="help-title">Nadpis</label>
            <n-input
              v-model:value="draft.title"
              :maxlength="127"
              :input-props="{ id: 'help-title' }"
            />
          </div>
          <HtmlEditor v-model:value="draft.content" :upload-image="uploadImage" />
          <div class="row">
            <n-button type="primary" :loading="saving" @click="save">Uložit</n-button>
            <n-button @click="editing = false">Zrušit</n-button>
          </div>
        </template>
        <template v-else>
          <div class="row">
            <p class="eyebrow">Nápověda</p>
            <span class="spacer" />
            <n-button v-if="auth.isBudkar" size="small" @click="edit">
              <template #icon><AppIcon name="edit" /></template>
              Upravit
            </n-button>
          </div>
          <h1>{{ helpTitle(article) }}</h1>
          <HtmlText
            v-if="article.content"
            :html="article.content"
            @help="router.push({ name: 'help_article', params: { slug: $event } })"
          />
          <p v-else class="muted">Tahle nápověda se teprve píše.</p>
        </template>
      </article>
      <p v-else class="muted">Tahle nápověda neexistuje.</p>
    </div>
    <p v-else class="muted">Načítám…</p>
  </main>
</template>

<style scoped>
.help-page {
  max-width: 1080px;
}

.article-layout {
  display: grid;
  grid-template-columns: 240px minmax(0, 1fr);
  gap: 32px;
  align-items: start;
}

.toc {
  display: grid;
  gap: 2px;
  position: sticky;
  top: 16px;
}

.toc .eyebrow {
  padding: 0 12px 8px;
}

.toc a {
  padding: 8px 12px;
  border-radius: var(--r-in);
  color: var(--text);
  text-decoration: none;
  font-weight: 600;
}

.toc a.on {
  background: var(--primary-soft);
  color: var(--primary-text);
}

.prose {
  display: grid;
  gap: 16px;
  max-width: 72ch;
  font-size: 16px;
  min-width: 0;
}

@media (max-width: 720px) {
  .article-layout {
    grid-template-columns: minmax(0, 1fr);
    gap: 20px;
  }

  .toc {
    position: static;
    display: flex;
    overflow-x: auto;
    gap: 6px;
  }

  .toc .eyebrow {
    display: none;
  }

  .toc a {
    white-space: nowrap;
    border: 1px solid var(--line);
  }
}
</style>
