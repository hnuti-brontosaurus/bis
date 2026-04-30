import { defineByIdStore } from "./factory.js"
import * as api from "@/api/chefs.js"

export const useChefsStore = defineByIdStore("chefs", api)
