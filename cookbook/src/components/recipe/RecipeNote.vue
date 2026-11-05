<script setup>
import { NButton, NH2, NText } from "naive-ui"
import { computed, ref, watch } from "vue"
import { storeToRefs } from "pinia"
import { faPen, faPlus } from "@fortawesome/free-solid-svg-icons"
import { icon } from "@/contrib/composables/render.js"
import { handleAxiosError } from "@/contrib/composables/setup.js"
import { recipeNotesApi } from "@/data/recipeComments.js"
import { useAuthStore } from "@/data/auth.js"
import { useRequireLogin } from "@/composables/requireLogin.js"
import { _ } from "@/composables/translations.js"
import HtmlText from "@/components/app/HtmlText.vue"
import RecipePhotos from "@/components/recipe/RecipePhotos.vue"
import WriteDialog from "@/components/recipe/WriteDialog.vue"

const props = defineProps({ recipe: { type: Object, required: true } })

const { isAuthenticated } = storeToRefs(useAuthStore())
const requireLogin = useRequireLogin()
const note = ref(null)
const writing = ref(false)

watch(
  [() => props.recipe.id, isAuthenticated],
  async () => {
    note.value = null
    if (!isAuthenticated.value) return
    try {
      note.value = await recipeNotesApi.get(props.recipe.id)
    } catch (e) {
      handleAxiosError(_.value.notes.load_error)(e)
    }
  },
  { immediate: true },
)

const initial = computed(() => ({
  id: note.value?.id,
  note: note.value?.note ?? "",
  photos: note.value?.photos ?? [],
}))

const write = () => {
  if (requireLogin()) writing.value = true
}

const save = async value => {
  note.value = await recipeNotesApi.save({ ...value, recipe_id: props.recipe.id })
}
</script>

<template>
  <section>
    <div class="title-row">
      <n-h2>{{ _.notes.title }}</n-h2>
      <n-button size="small" :render-icon="icon(note ? faPen : faPlus)" @click="write">
        {{ note ? _.notes.edit : _.notes.add }}
      </n-button>
    </div>
    <div v-if="note" class="note">
      <HtmlText v-if="note.note" :html="note.note" />
      <RecipePhotos
        v-if="note.photos.length"
        :photos="note.photos"
        :alt="recipe.name"
      />
    </div>
    <n-text v-else depth="3">{{ _.notes.hint }}</n-text>
    <WriteDialog
      v-model:show="writing"
      :title="_.notes.title"
      group="RecipeNote"
      text-key="note"
      :initial="initial"
      :save="save"
    >
      <n-text depth="3">{{ _.notes.dialog_hint }}</n-text>
    </WriteDialog>
  </section>
</template>

<style scoped>
.note {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-width: 66ch;
  padding: 10px 14px;
  border-left: 4px solid var(--primary);
  border-radius: 0 3px 3px 0;
  background: var(--primary-soft);
}
</style>
