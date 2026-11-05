import { fetchAll, upsert } from "./client.js"
import { defineByIdStore } from "./factory.js"

export const recipeTagsApi = {
  list: () => fetchAll("/recipe_tags/"),
  save: payload => upsert("/recipe_tags", payload),
}

export const useRecipeTagsStore = defineByIdStore("recipe_tags", recipeTagsApi)
