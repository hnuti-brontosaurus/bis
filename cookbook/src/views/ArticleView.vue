<script setup>
import { NButton } from "naive-ui"
import { faPen } from "@fortawesome/free-solid-svg-icons"
import { storeToRefs } from "pinia"
import { ref, watch } from "vue"
import AppPage from "@/components/app/AppPage.vue"
import HtmlText from "@/components/app/HtmlText.vue"
import HtmlEditor from "@/contrib/components/HtmlEditor.vue"
import { useRender } from "@/contrib/composables/render.js"
import { handleAxiosError } from "@/contrib/composables/setup.js"
import { _ } from "@/composables/translations.js"
import { useAuthStore } from "@/data/auth.js"
import { getArticle, saveArticle, uploadArticleImage } from "@/data/articles.js"

const props = defineProps({ slug: { type: String, required: true } })

const { icon } = useRender()
const { isEditor } = storeToRefs(useAuthStore())

const article = ref(null)
const draft = ref(null)

// Every article route renders this view, so moving between articles
// reuses the instance.
watch(
  () => props.slug,
  async slug => {
    article.value = null
    draft.value = null
    article.value = await getArticle(slug)
  },
  { immediate: true },
)

const save = async () => {
  try {
    article.value = await saveArticle({ slug: props.slug, content: draft.value })
    draft.value = null
  } catch (e) {
    handleAxiosError(_.value.common.save_error)(e)
  }
}
</script>

<template>
  <AppPage :title="_.menu[slug]">
    <template v-if="isEditor && article" #actions>
      <template v-if="draft !== null">
        <n-button type="primary" @click="save">{{ _.common.save }}</n-button>
        <n-button @click="draft = null">{{ _.common.clear }}</n-button>
      </template>
      <n-button v-else :render-icon="icon(faPen)" @click="draft = article.content">{{
        _.article.edit
      }}</n-button>
    </template>
    <div v-if="article" class="article">
      <HtmlEditor
        v-if="draft !== null"
        v-model:value="draft"
        rich
        :upload-image="image => uploadArticleImage(slug, image)"
      />
      <HtmlText v-else-if="article.content" :html="article.content" />
      <p v-else class="muted">{{ _.article.empty }}</p>
    </div>
  </AppPage>
</template>

<style scoped>
.article {
  max-width: 760px;
}
</style>
