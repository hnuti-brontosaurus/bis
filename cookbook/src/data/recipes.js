import { computed, unref } from "vue"
import { crudApi } from "./client.js"
import { defineByIdStore } from "./factory.js"
import { useChefsStore } from "./chefs.js"
import { useIngredientsStore } from "./ingredients.js"
import { useUnitsStore } from "./units.js"
import { useRecipeDifficultiesStore } from "./recipeDifficulties.js"
import { useRecipeRequiredTimesStore } from "./recipeRequiredTimes.js"
import { useRecipeTagsStore } from "./recipeTags.js"

export const recipesApi = crudApi("/recipes")

/**
 * Recipes are persisted by default for instant load. Image upload blobs
 * (`base64data` / `file`) are stripped before write — they appear only
 * mid-upload and are megabytes each. The `{small, medium, large, original}`
 * URLs returned by the backend are kept (they're just strings).
 */
const UPLOAD_BLOB_KEYS = ["base64data", "file"]
const stripUploadBlobs = recipe => {
  if (!recipe?.photo || typeof recipe.photo !== "object") return recipe
  const photo = Object.fromEntries(
    Object.entries(recipe.photo).filter(([k]) => !UPLOAD_BLOB_KEYS.includes(k)),
  )
  return { ...recipe, photo }
}

export const useRecipesStore = defineByIdStore("recipes", recipesApi, {
  serialize: stripUploadBlobs,
})

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

  return computed(() => {
    const raw = recipesStore.byId[unref(id)]
    if (!raw) return null
    return {
      ...raw,
      chef: chefsStore.byId[raw.chef_id],
      difficulty: difficultiesStore.byId[raw.difficulty_id],
      required_time: requiredTimesStore.byId[raw.required_time_id],
      tags: (raw.tag_ids ?? []).map(tagId => tagsStore.byId[tagId]).filter(Boolean),
      ingredients: (raw.ingredients ?? []).map(row => ({
        ...row,
        ingredient: ingredientsStore.byId[row.ingredient_id],
        unit: unitsStore.byId[row.unit_id],
      })),
    }
  })
}
