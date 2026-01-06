<script setup>
import {
  NFlex,
  NH1,
  NForm,
  NFormItem,
  NTag,
  NList,
  NText,
  NSelect,
  NPageHeader,
  NButton,
  NListItem,
  NButtonGroup,
  NCard,
  NInput,
  NInputGroup,
  NImage,
  NH2,
  NGridItem,
  NGrid,
  NInputNumber,
  NDataTable,
  useThemeVars,
} from "naive-ui"
import { rand, refDefault, toRefs } from "@vueuse/core"
import {
  chefs,
  dataIdMapping,
  dataOptions,
  recipe_difficulties,
  recipe_required_times,
  recipe_tags,
  recipes,
  useConnector,
} from "@/composables/connector.js"
import { useRoute, useRouter } from "vue-router"
import { computed, onMounted, ref, toRef } from "vue"
import RecipeIngrediences from "@/components/recipe/RecipeIngrediences.vue"
import RecipeSteps from "@/components/recipe/RecipeSteps.vue"
import { servings } from "@/composables/servings.js"
import CollapseList from "@/contrib/components/CollapseList.vue"
import { useRender } from "@/contrib/composables/render.js"
import { faCartPlus } from "@fortawesome/free-solid-svg-icons"
import AppPage from "@/components/app/AppPage.vue"
import { propertyRef } from "@/contrib/composables/helpers.js"
import GenericForm from "@/contrib/components/GenericForm.vue"
import { me } from "@/composables/auth.js"
import { _ } from "@/composables/translations.js"
import { handleAxiosError } from "@/contrib/composables/setup.js"

const route = useRoute()
const router = useRouter()
const { icon } = useRender()
const form = ref()

const recipe_id = route.params.id

if (recipe_id) useConnector("recipes", route.params.id)
useConnector("recipe_difficulties")
useConnector("recipe_required_times")
useConnector("recipe_tags")
useConnector("chefs")
useConnector("units")
useConnector("ingredients")
const connector = useConnector("recipes", false)

const recipe = recipe_id
  ? propertyRef(recipes, recipe_id)
  : ref({
      tags: [],
    })

const tagIds = computed(() => recipe.value.tags.map(_ => _.id))
const tagGroups = computed(() => [
  ...new Set(
    Object.values(recipe_tags.value)
      .sort((a, b) => a.order - b.order)
      .map(tag => tag.group),
  ),
])
const inputs = computed(() => [
  { type: "text", key: "name", required: true },
  {
    type: "select",
    key: "chef",
    required: "object",
    options: dataOptions(chefs),
    value: dataIdMapping(chefs, propertyRef(recipe, "chef")),
  },
  {
    type: "select",
    key: "difficulty",
    required: "object",
    options: dataOptions(recipe_difficulties),
    value: dataIdMapping(recipe_difficulties, propertyRef(recipe, "difficulty")),
  },
  {
    type: "select",
    key: "required_time",
    required: "object",
    options: dataOptions(recipe_required_times),
    value: dataIdMapping(recipe_required_times, propertyRef(recipe, "required_time")),
  },
  {
    type: "image",
    key: "photo",
    required: true,
  },
  {
    type: "checkboxes",
    checkboxes: [
      {
        key: "is_public",
        label: _.value.Recipe.is_public,
      },
    ],
  },
  ...tagGroups.value.map(group => ({
    type: "checkboxes",
    vertical: true,
    title: group,
    checkboxes: Object.values(recipe_tags.value)
      .filter(tag => tag.group === group)
      .map(tag => ({
        key: tag.id,
        label: tag.name,
        value: computed({
          get: () => tagIds.value.includes(tag.id),
          set: value => {
            if (value && !tagIds.value.includes(tag.id)) recipe.value.tags.push(tag)
            if (!value)
              recipe.value.tags = recipe.value.tags.filter(_ => _.id !== tag.id)
          },
        }),
      })),
  })),
  {
    type: "text",
    key: "intro",
    required: true,
    new_line: true,
    extra: { type: "textarea" },
  },
  {
    type: "text",
    key: "sources",
    required: true,
    extra: { type: "textarea" },
  },
  {
    title: _.value.Recipe.ingredients,
    hide_label: true,
    type: "section",
    key: "ingredients",
    span: 2,
  },
  {
    title: _.value.Recipe.steps,
    hide_label: true,
    type: "section",
    key: "steps",
    span: 2,
  },
  {
    title: _.value.Recipe.tips,
    hide_label: true,
    type: "section",
    key: "tips",
    span: 2,
  },
])

const save = async () => {
  try {
    await form.value.validate()
    const response = await connector.upsert(recipe.value)
    await connector.refresh(response.id)
    router.push({ name: "recipe", params: { id: response.id } })
  } catch (e) {
    console.log(e)
    handleAxiosError(_.value.edit_recipe.save_error)(e)
  }
}
</script>

<template>
  <AppPage :title="recipe_id ? 'Úprava receptu' : 'Nový recept'">
    <template #actions>
      <n-button @click="save">{{ _.edit_recipe.save }}</n-button>
    </template>
    {{ recipe }}
    <n-form ref="form" :model="recipe" @keydown.enter="save">
      <GenericForm v-model:data="recipe" :inputs="inputs" group="Recipe" />
    </n-form>
  </AppPage>
</template>

<style scoped></style>
