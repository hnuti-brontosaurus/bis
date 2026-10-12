import { computed, unref } from "vue"
import { crudApi } from "./client.js"
import { defineByIdStore } from "./factory.js"
import { useChefsStore } from "./chefs.js"
import { useIngredientsStore } from "./ingredients.js"
import { useUnitsStore } from "./units.js"
import { useRecipeDifficultiesStore } from "./recipeDifficulties.js"
import { useRecipeRequiredTimesStore } from "./recipeRequiredTimes.js"
import { useRecipeTagsStore } from "./recipeTags.js"
import { useAllergensStore } from "./allergens.js"

export const recipesApi = crudApi("/recipes")

export const useRecipesStore = defineByIdStore("recipes", recipesApi)

/**
 * Resolve a recipe's `_id` references to objects from sibling stores.
 * Returns a computed wrapper that spreads the raw row plus
 * `chef`, `difficulty`, `required_time`, `tags`, and per-ingredient
 * `ingredient`/`unit` resolved against the relevant byId maps.
 *
 * Pass either an id (number/string) or a ref/computed yielding one.
 */
export const useRecipe = id => {
  const recipesStore = useRecipesStore()
  const chefsStore = useChefsStore()
  const difficultiesStore = useRecipeDifficultiesStore()
  const requiredTimesStore = useRecipeRequiredTimesStore()
  const tagsStore = useRecipeTagsStore()
  const ingredientsStore = useIngredientsStore()
  const unitsStore = useUnitsStore()
  const allergensStore = useAllergensStore()

  return computed(() => {
    const raw = recipesStore.byId[unref(id)]
    if (!raw) return null
    return {
      ...raw,
      chef: chefsStore.byId[raw.chef_id],
      difficulty: difficultiesStore.byId[raw.difficulty_id],
      required_time: requiredTimesStore.byId[raw.required_time_id],
      tags: (raw.tag_ids ?? []).map(tagId => tagsStore.byId[tagId]).filter(Boolean),
      allergens: (raw.allergen_ids ?? [])
        .map(id => allergensStore.byId[id])
        .filter(Boolean),
      ingredients: (raw.ingredients ?? []).map(row => ({
        ...row,
        ingredient: ingredientsStore.byId[row.ingredient_id],
        unit: unitsStore.byId[row.unit_id],
      })),
    }
  })
}
