<script setup>
import { NForm, NButton, NH2, NSwitch, useDialog } from "naive-ui"
import { faCheck, faTrash } from "@fortawesome/free-solid-svg-icons"
import { icon } from "@/contrib/composables/render.js"
import { computed, onMounted, ref, watch } from "vue"
import { useRoute, useRouter } from "vue-router"
import { storeToRefs } from "pinia"
import axios from "axios"
import AppPage from "@/components/app/AppPage.vue"
import UploadPhotosDialog from "@/components/UploadPhotosDialog.vue"
import { propertyRef, scrollToFirstFormError } from "@/contrib/composables/helpers.js"
import GenericForm from "@/contrib/components/GenericForm.vue"
import { _ } from "@/composables/translations.js"
import { handleAxiosError } from "@/contrib/composables/setup.js"
import { useRecipeSave } from "@/composables/useRecipeSave.js"
import { useRecipesStore } from "@/data/recipes.js"
import { useChefsStore } from "@/data/chefs.js"
import { useRecipeDifficultiesStore } from "@/data/recipeDifficulties.js"
import { useRecipeRequiredTimesStore } from "@/data/recipeRequiredTimes.js"
import { useRecipeTagsStore } from "@/data/recipeTags.js"
import { useUnitsStore } from "@/data/units.js"
import { useIngredientsStore } from "@/data/ingredients.js"
import { useAuthStore } from "@/data/auth.js"
import { storeOptions } from "@/data/helpers.js"
import { withPartHeadings, withoutPartHeadings } from "@/data/ingredientParts.js"

const route = useRoute()
const router = useRouter()
const dialog = useDialog()
const form = ref()

const recipesStore = useRecipesStore()
const chefsStore = useChefsStore()
const difficultiesStore = useRecipeDifficultiesStore()
const requiredTimesStore = useRecipeRequiredTimesStore()
const tagsStore = useRecipeTagsStore()
const { isEditor, chefId } = storeToRefs(useAuthStore())
useUnitsStore().fetchAll()
useIngredientsStore().fetchAll()

const recipe_id = route.params.id

// A local working copy of the recipe (shallow ref). Initialised after
// fetchOne settles for edit mode, or pre-populated for create mode.
// On create, default chef_id to the logged-in chef so non-editor chefs
// don't have to pick (and can't pick a different one — the dropdown is
// hidden for them, see `inputs` below).
const recipe = ref(
  recipe_id
    ? null
    : {
        tag_ids: [],
        ingredients: [],
        steps: [],
        tips: [],
        chef_id: chefId.value,
      },
)

onMounted(async () => {
  await Promise.all([
    chefsStore.fetchAll(),
    difficultiesStore.fetchAll(),
    requiredTimesStore.fetchAll(),
    tagsStore.fetchAll(),
  ])
  if (recipe_id) {
    const fresh = await recipesStore.fetchOne(recipe_id)
    // Mirror backend _can_write: editor edits any; chef edits only own.
    if (!isEditor.value && fresh.chef_id !== chefId.value) {
      router.replace({ name: "recipe", params: { id: recipe_id } })
      return
    }
    // Local working copy — deep-cloned so edits don't mutate cache directly.
    recipe.value = JSON.parse(JSON.stringify(fresh))
    ingredientRows.value = withPartHeadings(recipe.value.ingredients)
  }
})

const ingredientRows = ref([])

const tagIds = computed(() => recipe.value?.tag_ids ?? [])
const tagGroups = computed(() => [
  ...new Set(
    tagsStore.list
      .slice()
      .sort((a, b) => a.order - b.order)
      .map(tag => tag.group),
  ),
])

const basicInputs = computed(() => {
  // Photo / intro / sources are required only when publishing the recipe;
  // non-public recipes can be saved as drafts without them. Backend mirrors
  // this in RecipeSerializer.validate.
  const publishedRequired = !!recipe.value.is_public
  return [
    { type: "text", key: "name", required: true, span: 2 },
    // Only editors get to pick the chef; for plain chefs the field is
    // hidden and locked to their own chef_id by the onMounted guard.
    isEditor.value && {
      type: "select",
      key: "chef",
      path: "chef_id",
      required: "number",
      options: storeOptions(chefsStore).value,
      value: propertyRef(recipe, "chef_id"),
    },
    {
      type: "select",
      key: "difficulty",
      path: "difficulty_id",
      required: "number",
      options: storeOptions(difficultiesStore).value,
      value: propertyRef(recipe, "difficulty_id"),
    },
    {
      type: "select",
      key: "required_time",
      path: "required_time_id",
      required: "number",
      options: storeOptions(requiredTimesStore).value,
      value: propertyRef(recipe, "required_time_id"),
    },
    { type: "image", key: "photo", required: publishedRequired },
    {
      type: "text",
      key: "intro",
      required: publishedRequired,
      span: 2,
      extra: { type: "textarea" },
    },
    {
      type: "text",
      key: "sources",
      required: publishedRequired,
      span: 2,
      extra: { type: "textarea" },
    },
  ].filter(Boolean)
})

const tagInputs = computed(() =>
  tagGroups.value.map(group => ({
    type: "checkboxes",
    vertical: true,
    title: group,
    checkboxes: tagsStore.list
      .filter(tag => tag.group === group)
      .map(tag => ({
        key: tag.id,
        label: tag.name,
        value: computed({
          get: () => tagIds.value.includes(tag.id),
          set: value => {
            if (value && !tagIds.value.includes(tag.id))
              recipe.value.tag_ids.push(tag.id)
            if (!value)
              recipe.value.tag_ids = recipe.value.tag_ids.filter(id => id !== tag.id)
          },
        }),
      })),
  })),
)

const sectionInputs = computed(() => [
  {
    title: _.value.recipes.ingredients,
    hide_label: true,
    type: "section",
    hide_feedback: true,
    key: "ingredients",
    value: ingredientRows,
    span: 2,
  },
  {
    title: _.value.recipes.steps,
    hide_label: true,
    type: "section",
    hide_feedback: true,
    key: "steps",
    span: 2,
  },
  {
    title: _.value.recipes.tips,
    hide_label: true,
    type: "section",
    hide_feedback: true,
    key: "tips",
    span: 2,
  },
])

// Per-field backend errors keyed by field name. GenericForm renders
// non_field_errors as an alert and scrolls to the first invalid field
// whenever this object changes.
const backendErrors = ref({})
const fieldErrors = computed(() =>
  Object.fromEntries(
    Object.entries(backendErrors.value).filter(([key]) => key !== "non_field_errors"),
  ),
)

const onDelete = () => {
  dialog.warning({
    title: _.value.recipes.delete_title,
    content: _.value.recipes.delete_content,
    positiveText: _.value.recipes.delete,
    negativeText: _.value.common.back,
    onPositiveClick: async () => {
      try {
        await recipesStore.remove(recipe.value.id)
        router.push({ name: "recipes" })
      } catch (e) {
        handleAxiosError(_.value.recipes.delete_error)(e)
      }
    },
  })
}

const upload = useRecipeSave()
const showUploadDialog = ref(false)

// When the orchestrator finishes (initial run or after a retry), navigate
// to the saved recipe. Stays on the edit page if any photo failed.
watch(
  () => upload.state.phase,
  phase => {
    if (phase === "done" && upload.state.recipeId) {
      showUploadDialog.value = false
      router.push({ name: "recipe", params: { id: upload.state.recipeId } })
    }
  },
)

const save = async () => {
  backendErrors.value = {}
  try {
    await form.value.validate()
    // `order` mirrors the list position the user sees; assign it here so
    // reordering in the dynamic-input UI is what gets persisted.
    recipe.value.ingredients = withoutPartHeadings(ingredientRows.value)
    recipe.value.steps.forEach((row, i) => (row.order = i))

    showUploadDialog.value = true
    await upload.run(recipe.value)
    // The watcher above handles navigation on done; if the run finishes
    // in 'partial' the modal stays open with retry buttons.
  } catch (e) {
    showUploadDialog.value = false
    if (axios.isAxiosError(e) && e.response?.status === 400 && e.response.data) {
      backendErrors.value = e.response.data
    } else {
      // Client-side validation failure — backendErrors watcher won't fire,
      // scroll explicitly so the user sees the offending field.
      scrollToFirstFormError()
    }
    handleAxiosError(_.value.edit_recipe.save_error)(e)
  }
}
</script>

<template>
  <AppPage :title="recipe_id ? _.edit_recipe.title_edit : _.edit_recipe.title_new">
    <template v-if="recipe" #actions>
      <n-switch
        :value="!!recipe.is_public"
        @update:value="v => (recipe.is_public = v)"
        :round="false"
      >
        <template #checked>{{ _.recipes.is_public }}</template>
        <template #unchecked>{{ _.recipes.is_private }}</template>
      </n-switch>
      <n-button type="primary" :render-icon="icon(faCheck)" @click="save">{{
        _.edit_recipe.save
      }}</n-button>
      <n-button
        v-if="recipe_id"
        type="error"
        ghost
        :render-icon="icon(faTrash)"
        @click="onDelete"
        >{{ _.recipes.delete }}</n-button
      >
    </template>
    <n-form v-if="recipe" ref="form" :model="recipe" class="form">
      <section class="panel">
        <GenericForm
          v-model:data="recipe"
          :inputs="basicInputs"
          :backend-errors="backendErrors"
          group="Recipe"
        />
      </section>
      <section v-if="tagInputs.length" class="panel">
        <n-h2>{{ _.recipes.tags }}</n-h2>
        <GenericForm
          v-model:data="recipe"
          :inputs="tagInputs"
          :backend-errors="fieldErrors"
          group="Recipe"
        />
      </section>
      <section v-for="input in sectionInputs" :key="input.key" class="panel">
        <GenericForm
          v-model:data="recipe"
          :inputs="[input]"
          :backend-errors="fieldErrors"
          group="Recipe"
        />
      </section>
    </n-form>
    <UploadPhotosDialog
      v-model:show="showUploadDialog"
      :state="upload.state"
      @retry="upload.retryFailed"
    />
  </AppPage>
</template>

<style scoped>
.form {
  display: flex;
  flex-direction: column;
  gap: 22px;
}
</style>
