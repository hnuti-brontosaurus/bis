import { fetchAll } from "./client.js"
import { defineByIdStore } from "./factory.js"

export const ingredientCategoriesApi = {
  list: () => fetchAll("/ingredient_categories/"),
}

export const useIngredientCategoriesStore = defineByIdStore(
  "ingredient_categories",
  ingredientCategoriesApi,
)
