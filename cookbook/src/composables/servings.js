import { useLocalStorage } from "@vueuse/core"

export const servings = useLocalStorage("servings", 2)
