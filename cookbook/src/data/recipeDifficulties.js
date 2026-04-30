import { fetchAll } from "./client.js"
import { defineByIdStore } from "./factory.js"

export const recipeDifficultiesApi = { list: () => fetchAll("/recipe_difficulties/") }

export const useRecipeDifficultiesStore = defineByIdStore(
  "recipe_difficulties",
  recipeDifficultiesApi,
)
