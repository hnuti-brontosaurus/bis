import { crudApi } from "./client.js"
import { defineByIdStore } from "./factory.js"

export const menusApi = crudApi("/menus")

export const useMenusStore = defineByIdStore("menus", menusApi)
