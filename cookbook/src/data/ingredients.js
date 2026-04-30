import { crudApi } from "./client.js"
import { defineByIdStore } from "./factory.js"

export const ingredientsApi = crudApi("/ingredients")

export const useIngredientsStore = defineByIdStore("ingredients", ingredientsApi)
