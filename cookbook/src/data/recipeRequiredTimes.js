import { fetchAll } from "./client.js"
import { defineByIdStore } from "./factory.js"

export const recipeRequiredTimesApi = {
  list: () => fetchAll("/recipe_required_times/"),
}

export const useRecipeRequiredTimesStore = defineByIdStore(
  "recipe_required_times",
  recipeRequiredTimesApi,
)
