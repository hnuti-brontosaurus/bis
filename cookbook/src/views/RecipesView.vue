<script setup>
import {
  NFlex,
  NButtonGroup,
  NPageHeader,
  NButton,
  NGrid,
  NGridItem,
  NCard,
  NInput,
  NEmpty,
  NBadge,
} from "naive-ui"
import { computed, onMounted, ref } from "vue"
import { useRouter } from "vue-router"
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome"
import { faEyeSlash, faSearch } from "@fortawesome/free-solid-svg-icons"
import { useRecipesStore } from "@/data/recipes.js"
import { useChefsStore } from "@/data/chefs.js"
import { useIngredientsStore } from "@/data/ingredients.js"
import { useRecipeTagsStore } from "@/data/recipeTags.js"
import { useAllergensStore } from "@/data/allergens.js"
import { useRecipeDifficultiesStore } from "@/data/recipeDifficulties.js"
import { useRecipeRequiredTimesStore } from "@/data/recipeRequiredTimes.js"
import { useRecipeFilters } from "@/composables/recipeFilters.js"
import RecipeFiltersDrawer from "@/components/recipe/RecipeFiltersDrawer.vue"
import RecipeFiltersSummary from "@/components/recipe/RecipeFiltersSummary.vue"
import { _ } from "@/composables/translations.js"

const recipesStore = useRecipesStore()
const chefsStore = useChefsStore()
const ingredientsStore = useIngredientsStore()
const tagsStore = useRecipeTagsStore()
const allergensStore = useAllergensStore()
const difficultiesStore = useRecipeDifficultiesStore()
const requiredTimesStore = useRecipeRequiredTimesStore()

onMounted(() => {
  recipesStore.fetchAll()
  chefsStore.fetchAll()
  ingredientsStore.fetchAll()
  tagsStore.fetchAll()
  allergensStore.fetchAll()
  difficultiesStore.fetchAll()
  requiredTimesStore.fetchAll()
})

const router = useRouter()

const onClick = id => router.push({ name: "recipe", params: { id } })

const chefNameFor = chef_id => computed(() => chefsStore.byId[chef_id]?.name ?? "")

const { filters, filteredRecipes, isActive } = useRecipeFilters()

const drawerOpen = ref(false)

const activeFilterCount = computed(() => {
  const f = filters.value
  let n = 0
  if (f.search.trim()) n++
  n += f.chef_ids.length
  n += f.difficulty_ids.length
  n += f.required_time_ids.length
  n += f.tag_ids_include.length
  n += f.tag_ids_exclude.length
  n += f.allergen_ids_exclude.length
  n += f.ingredient_ids_include.length
  n += f.ingredient_ids_exclude.length
  if (f.visibility !== "all") n++
  return n
})
</script>

<template>
  <n-flex vertical>
    <n-page-header :title="_.Recipe.plural">
      <template #extra>
        <n-flex align="center" justify="end" :size="8">
          <n-button-group>
            <n-button @click="router.push({ name: 'create_recipe' })">{{
              _.recipes.create
            }}</n-button>
            <n-badge
              :value="activeFilterCount"
              :show="activeFilterCount > 0"
              :offset="[-6, 4]"
            >
              <n-button @click="drawerOpen = true">{{ _.common.filters }}</n-button>
            </n-badge>
          </n-button-group>
          <n-input
            v-model:value="filters.search"
            :placeholder="_.recipes.search_placeholder"
            clearable
            style="min-width: 200px; flex: 0 1 240px"
          >
            <template #prefix>
              <font-awesome-icon :icon="faSearch" />
            </template>
          </n-input>
        </n-flex>
      </template>
    </n-page-header>

    <recipe-filters-summary />

    <n-empty
      v-if="isActive && filteredRecipes.length === 0"
      :description="_.recipes.no_results"
    />

    <n-grid cols="1 s:2 m:3" x-gap="32" y-gap="32" responsive="screen">
      <n-grid-item v-for="recipe in filteredRecipes" :key="recipe.id">
        <router-link :to="{ name: 'recipe', params: { id: recipe.id } }" custom>
          <n-card
            :title="recipe.name"
            embedded
            hoverable
            style="cursor: pointer"
            @click="onClick(recipe.id)"
          >
            <template #cover>
              <div style="position: relative">
                <img
                  :src="recipe.photo?.medium"
                  :alt="recipe.name"
                  style="object-fit: cover; height: 200px; width: 100%"
                />
                <div
                  v-if="!recipe.is_public"
                  :title="_.recipes.is_private"
                  style="
                    position: absolute;
                    top: 8px;
                    right: 8px;
                    background: rgba(0, 0, 0, 0.6);
                    color: white;
                    padding: 4px 8px;
                    border-radius: 4px;
                    line-height: 1;
                  "
                >
                  <font-awesome-icon :icon="faEyeSlash" />
                </div>
              </div>
            </template>
            {{ chefNameFor(recipe.chef_id).value }}
          </n-card>
        </router-link>
      </n-grid-item>
    </n-grid>

    <recipe-filters-drawer v-model:show="drawerOpen" />
  </n-flex>
</template>

<style scoped></style>
