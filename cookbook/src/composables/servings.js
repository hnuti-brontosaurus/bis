import { computed, toRef } from "vue"
import { useMessage } from "naive-ui"
import { toRefs, useLocalStorage, useThrottleFn } from "@vueuse/core"
import axios from "axios"

export const servings = useLocalStorage("servings", 2)
