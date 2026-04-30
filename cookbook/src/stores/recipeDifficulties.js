import { defineByIdStore } from "./factory.js"
import * as api from "@/api/recipeDifficulties.js"

export const useRecipeDifficultiesStore = defineByIdStore("recipe_difficulties", api)
