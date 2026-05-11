<script setup>
import { NTag, NFlex, NButton, NText } from "naive-ui"
import { computed } from "vue"
import { useRecipeFilters } from "@/composables/recipeFilters.js"
import { useChefsStore } from "@/data/chefs.js"
import { useIngredientsStore } from "@/data/ingredients.js"
import { useRecipeTagsStore } from "@/data/recipeTags.js"
import { useAllergensStore } from "@/data/allergens.js"
import { useRecipeDifficultiesStore } from "@/data/recipeDifficulties.js"
import { useRecipeRequiredTimesStore } from "@/data/recipeRequiredTimes.js"
import { _ } from "@/composables/translations.js"

const { filters, isActive, reset } = useRecipeFilters()

const chefsStore = useChefsStore()
const ingredientsStore = useIngredientsStore()
const tagsStore = useRecipeTagsStore()
const allergensStore = useAllergensStore()
const difficultiesStore = useRecipeDifficultiesStore()
const requiredTimesStore = useRecipeRequiredTimesStore()

const nameById = (store, id) => store.byId[id]?.name ?? `#${id}`

const removeFromList = (key, id) => {
  filters.value[key] = filters.value[key].filter(x => x !== id)
}

const chips = computed(() => {
  const out = []
  const f = filters.value

  if (f.search.trim()) {
    out.push({
      key: `search:${f.search}`,
      label: `${_.value.recipes.search_label}: "${f.search}"`,
      onClose: () => (f.search = ""),
    })
  }

  const listFilter = (storeKey, store, prefix) => {
    for (const id of f[storeKey]) {
      out.push({
        key: `${storeKey}:${id}`,
        label: `${prefix}: ${nameById(store, id)}`,
        onClose: () => removeFromList(storeKey, id),
      })
    }
  }

  listFilter("chef_ids", chefsStore, _.value.recipes.chef)
  listFilter("difficulty_ids", difficultiesStore, _.value.recipes.difficulty)
  listFilter("required_time_ids", requiredTimesStore, _.value.recipes.required_time)
  listFilter("tag_ids_include", tagsStore, _.value.recipes.tags_include)
  listFilter("tag_ids_exclude", tagsStore, _.value.recipes.tags_exclude)
  listFilter("allergen_ids_exclude", allergensStore, _.value.recipes.allergens_exclude)
  listFilter(
    "ingredient_ids_include",
    ingredientsStore,
    _.value.recipes.ingredients_include,
  )
  listFilter(
    "ingredient_ids_exclude",
    ingredientsStore,
    _.value.recipes.ingredients_exclude,
  )

  if (f.visibility !== "all") {
    const label =
      f.visibility === "public" ? _.value.recipes.is_public : _.value.recipes.is_private
    out.push({
      key: "visibility",
      label: `${_.value.recipes.visibility}: ${label}`,
      onClose: () => (f.visibility = "all"),
    })
  }

  return out
})
</script>

<template>
  <n-flex v-if="isActive" align="center" :size="[8, 8]">
    <n-text depth="3">{{ _.recipes.active_filters }} ({{ chips.length }}):</n-text>
    <n-tag
      v-for="chip in chips"
      :key="chip.key"
      closable
      :bordered="false"
      type="info"
      @close="chip.onClose"
    >
      {{ chip.label }}
    </n-tag>
    <n-button size="small" tertiary @click="reset">{{
      _.recipes.clear_filters
    }}</n-button>
  </n-flex>
</template>
