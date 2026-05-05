import { crudApi } from "./client.js"
import { defineByIdStore } from "./factory.js"

export const chefsApi = crudApi("/chefs")

export const useChefsStore = defineByIdStore("chefs", chefsApi)
