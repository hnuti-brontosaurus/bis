import { defineByIdStore } from "./factory.js"
import * as api from "@/api/ingredients.js"

export const useIngredientsStore = defineByIdStore("ingredients", api)
