import { fetchAll } from "./client.js"
import { defineByIdStore } from "./factory.js"

export const recipeTagsApi = { list: () => fetchAll("/recipe_tags/") }

export const useRecipeTagsStore = defineByIdStore("recipe_tags", recipeTagsApi)
