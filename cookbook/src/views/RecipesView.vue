<script setup>
import { NFlex, NH1, NButton, NCard, NInput, NEmpty, NBadge, NTag } from "naive-ui"
import { computed, onMounted, ref } from "vue"
import { useRouter } from "vue-router"
import { useElementSize } from "@vueuse/core"
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome"
import {
  faEyeSlash,
  faFilter,
  faPlus,
  faSearch,
  faDumbbell,
} from "@fortawesome/free-solid-svg-icons"
import { faClock } from "@fortawesome/free-regular-svg-icons"
import { icon } from "@/contrib/composables/render.js"
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

const tagsOf = recipe => recipe.tag_ids.map(id => tagsStore.byId[id]).filter(Boolean)

const { filters, filteredRecipes, isActive } = useRecipeFilters()

const CARD_MIN_WIDTH = 250
const CARD_GAP = 24

const cardColumns = ref(null)
const { width } = useElementSize(cardColumns)

// Dealing the recipes out one per column keeps the reading order left to right
// while letting every card keep its own height, which CSS columns cannot do.
const recipeColumns = computed(() => {
  const count = Math.max(
    1,
    Math.floor((width.value + CARD_GAP) / (CARD_MIN_WIDTH + CARD_GAP)),
  )
  const columns = Array.from({ length: count }, () => [])
  filteredRecipes.value.forEach((recipe, index) => columns[index % count].push(recipe))
  return columns
})

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
  <n-flex vertical :size="22">
    <div class="title-row">
      <n-h1>{{ _.Recipe.plural }}</n-h1>
      <n-flex align="center" justify="end" :size="10" style="flex: 1">
        <n-input
          v-model:value="filters.search"
          :placeholder="_.recipes.search_placeholder"
          clearable
          style="min-width: 200px; flex: 0 1 300px"
        >
          <template #prefix>
            <font-awesome-icon :icon="faSearch" />
          </template>
        </n-input>
        <n-badge
          :value="activeFilterCount"
          :show="activeFilterCount > 0"
          :offset="[-6, 4]"
        >
          <n-button :render-icon="icon(faFilter)" @click="drawerOpen = true">{{
            _.common.filters
          }}</n-button>
        </n-badge>
        <n-button
          type="primary"
          :render-icon="icon(faPlus)"
          @click="router.push({ name: 'create_recipe' })"
          >{{ _.recipes.create }}</n-button
        >
      </n-flex>
    </div>

    <recipe-filters-summary />

    <n-empty
      v-if="isActive && filteredRecipes.length === 0"
      :description="_.recipes.no_results"
    />

    <div ref="cardColumns" class="card-columns">
      <div v-for="(column, index) in recipeColumns" :key="index" class="card-column">
        <router-link
          v-for="recipe in column"
          :key="recipe.id"
          :to="{ name: 'recipe', params: { id: recipe.id } }"
          custom
        >
          <n-card hoverable class="recipe-card" @click="onClick(recipe.id)">
            <template #cover>
              <div class="card-cover">
                <img
                  v-if="recipe.photo"
                  :src="recipe.photo.medium"
                  :alt="recipe.name"
                />
                <n-flex class="cover-tags" :size="6">
                  <n-tag
                    v-if="difficultiesStore.byId[recipe.difficulty_id]"
                    size="small"
                    :bordered="false"
                  >
                    <template #icon><font-awesome-icon :icon="faDumbbell" /></template>
                    {{ difficultiesStore.byId[recipe.difficulty_id].name }}
                  </n-tag>
                  <n-tag
                    v-if="requiredTimesStore.byId[recipe.required_time_id]"
                    size="small"
                    :bordered="false"
                  >
                    <template #icon><font-awesome-icon :icon="faClock" /></template>
                    {{ requiredTimesStore.byId[recipe.required_time_id].name }}
                  </n-tag>
                </n-flex>
                <div
                  v-if="!recipe.is_public"
                  class="private-mark"
                  :title="_.recipes.is_private"
                >
                  <font-awesome-icon :icon="faEyeSlash" />
                </div>
              </div>
            </template>
            <template #header>
              {{ recipe.name }}
              <div v-if="chefsStore.byId[recipe.chef_id]" class="chef">
                {{ chefsStore.byId[recipe.chef_id].name }}
              </div>
            </template>
            <template v-if="tagsOf(recipe).length" #footer>
              <n-flex :size="6">
                <n-tag v-for="tag in tagsOf(recipe)" :key="tag.id" size="small">{{
                  tag.name
                }}</n-tag>
              </n-flex>
            </template>
          </n-card>
        </router-link>
      </div>
    </div>

    <recipe-filters-drawer v-model:show="drawerOpen" />
  </n-flex>
</template>

<style scoped>
.card-columns {
  display: flex;
  align-items: flex-start;
  gap: 24px;
}

.card-column {
  display: flex;
  flex: 1 1 0;
  flex-direction: column;
  gap: 24px;
  min-width: 0;
}

.recipe-card {
  cursor: pointer;
}

.chef {
  margin-top: 4px;
  color: var(--muted);
  font-family: var(--font-body);
  font-size: 0.85em;
  font-weight: 400;
  letter-spacing: normal;
}

.cover-tags {
  position: absolute;
  bottom: 10px;
  left: 10px;
}

.cover-tags .n-tag {
  background: var(--surface);
  color: var(--text);
}

.private-mark {
  position: absolute;
  top: 10px;
  right: 10px;
  padding: 4px 7px;
  border-radius: 3px;
  background: var(--surface);
  color: var(--muted);
  line-height: 1;
  opacity: 0.85;
}
</style>
