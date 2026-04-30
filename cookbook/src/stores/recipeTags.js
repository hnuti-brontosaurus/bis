import { defineByIdStore } from "./factory.js"
import * as api from "@/api/recipeTags.js"

export const useRecipeTagsStore = defineByIdStore("recipe_tags", api)
