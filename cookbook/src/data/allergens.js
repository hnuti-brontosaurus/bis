import { fetchAll } from "./client.js"
import { defineByIdStore } from "./factory.js"

export const allergensApi = { list: () => fetchAll("/allergens/") }

export const useAllergensStore = defineByIdStore("allergens", allergensApi)
