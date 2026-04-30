import { defineByIdStore } from "./factory.js"
import * as api from "@/api/recipeRequiredTimes.js"

export const useRecipeRequiredTimesStore = defineByIdStore("recipe_required_times", api)
