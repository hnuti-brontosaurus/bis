import { fetchAll } from "./client.js"
import { defineByIdStore } from "./factory.js"

export const unitsApi = { list: () => fetchAll("/units/") }

export const useUnitsStore = defineByIdStore("units", unitsApi)
