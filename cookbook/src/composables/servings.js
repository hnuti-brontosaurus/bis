import {computed, toRef} from "vue";
import {useErrorHandler} from "@/contrib/composables/errorHandler.js";
import {useMessage} from "naive-ui";
import {toRefs, useLocalStorage, useThrottleFn} from "@vueuse/core";
import axios from "axios";

const count = useLocalStorage(
    "servings",
    2,
)


export const useServings = () => {
    return {count}
}
