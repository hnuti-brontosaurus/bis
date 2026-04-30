import { defineByIdStore } from "./factory.js"
import * as api from "@/api/recipes.js"

// Recipes carry photo dicts and large nested children — skip persistence.
export const useRecipesStore = defineByIdStore("recipes", api, { persist: false })
