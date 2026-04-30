import { defineByIdStore } from "./factory.js"
import * as api from "@/api/units.js"

export const useUnitsStore = defineByIdStore("units", api)
