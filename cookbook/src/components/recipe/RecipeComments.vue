<script setup>
import { NButton, NFlex, NH2, NSwitch, NTag, NText, useDialog } from "naive-ui"
import { ref, watch } from "vue"
import { faPlus, faTrash } from "@fortawesome/free-solid-svg-icons"
import { icon } from "@/contrib/composables/render.js"
import { handleAxiosError } from "@/contrib/composables/setup.js"
import { recipeCommentsApi } from "@/data/recipeComments.js"
import { useRequireLogin } from "@/composables/requireLogin.js"
import { _ } from "@/composables/translations.js"
import HtmlText from "@/components/app/HtmlText.vue"
import RecipePhotos from "@/components/recipe/RecipePhotos.vue"
import WriteDialog from "@/components/recipe/WriteDialog.vue"

const props = defineProps({ recipe: { type: Object, required: true } })

const dialog = useDialog()
const requireLogin = useRequireLogin()
const comments = ref([])
const writing = ref(false)

const load = async () => {
  try {
    comments.value = await recipeCommentsApi.list(props.recipe.id)
  } catch (e) {
    handleAxiosError(_.value.comments.load_error)(e)
  }
}
watch(() => props.recipe.id, load, { immediate: true })

const write = () => {
  if (requireLogin()) writing.value = true
}

const save = async comment => {
  await recipeCommentsApi.create({ ...comment, recipe_id: props.recipe.id })
  await load()
}

const remove = comment =>
  dialog.warning({
    title: _.value.comments.delete_title,
    content: _.value.comments.delete_content,
    positiveText: _.value.comments.delete,
    negativeText: _.value.common.back,
    onPositiveClick: async () => {
      try {
        await recipeCommentsApi.remove(comment.id)
        await load()
      } catch (e) {
        handleAxiosError(_.value.comments.delete_error)(e)
      }
    },
  })

const date = value => new Date(value).toLocaleDateString("cs-CZ")
</script>

<template>
  <section>
    <div class="title-row">
      <n-h2>{{ _.comments.title }}</n-h2>
      <n-button size="small" :render-icon="icon(faPlus)" @click="write">
        {{ _.comments.add }}
      </n-button>
    </div>
    <n-text v-if="!comments.length" depth="3">{{ _.comments.empty }}</n-text>
    <article v-for="comment in comments" :key="comment.id" class="comment">
      <n-flex align="center" :size="8">
        <strong>{{ comment.author }}</strong>
        <n-text depth="3">{{ date(comment.created_at) }}</n-text>
        <n-tag v-if="!comment.is_public" size="small" :bordered="false">
          {{ _.comments.private }}
        </n-tag>
        <n-button
          v-if="comment.can_delete"
          class="delete"
          size="tiny"
          quaternary
          :title="_.comments.delete"
          :render-icon="icon(faTrash)"
          @click="remove(comment)"
        />
      </n-flex>
      <HtmlText :html="comment.comment" />
      <RecipePhotos
        v-if="comment.photos.length"
        :photos="comment.photos"
        :alt="comment.author"
      />
    </article>
    <WriteDialog
      v-model:show="writing"
      :title="_.comments.add"
      group="RecipeComment"
      text-key="comment"
      text-required
      :initial="{ comment: '', is_public: true, photos: [] }"
      :save="save"
      v-slot="{ value }"
    >
      <n-flex v-if="value" align="center" :wrap="false">
        <n-switch v-model:value="value.is_public" :round="false">
          <template #checked>{{ _.comments.public }}</template>
          <template #unchecked>{{ _.comments.private }}</template>
        </n-switch>
        <n-text depth="3">{{
          value.is_public ? _.comments.public_hint : _.comments.private_hint
        }}</n-text>
      </n-flex>
    </WriteDialog>
  </section>
</template>

<style scoped>
.comment {
  display: flex;
  flex-direction: column;
  gap: 6px;
  max-width: 66ch;
  padding: 12px 0;
  border-bottom: 1px solid var(--line);
}

.delete {
  margin-left: auto;
}
</style>
