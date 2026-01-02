import {computed, onMounted, toRef} from "vue";
import {useErrorHandler} from "@/contrib/composables/errorHandler.js";
import {useMessage} from "naive-ui";
import {toRefs, useLocalStorage, useThrottleFn} from "@vueuse/core";
import axios from "axios";

const storage = useLocalStorage(
    "connector",
    {
        recipes: {},
        menus: {},
        chefs: {},
        units: {},
        ingredients: {},
        recipe_difficulties: {},
        recipe_tags: {},
    },
    {mergeDefaults: true},
)


export const useConnector = (name, autoFetch=true) => {
    const {handleAxiosError} = useErrorHandler()
    const message = useMessage()
    const local_data = toRefs(storage)[name]

    const do_fetch = (name, url, ids = []) => {
        axios.get(url).then(({data}) => {
            let results = data.results
            if (!Array.isArray(results)) {
                local_data.value[data.id] = data
                return
            }
            results.forEach(row => storage.value[name][row.id] = row)
            ids = ids.concat(results.map(row => row.id))
            if (data.next) {
                do_fetch(name, data.next, ids)
            } else {
                ids = new Set(ids.map(id => id.toString()))
                for (const key of Object.keys(local_data.value)) {
                    if (!ids.has(key)){
                        delete local_data.value[key];
                    }
                }
            }
        }).catch(handleAxiosError(`Error fetching ${name}`))
    }

    const fetch = useThrottleFn(() => {
        do_fetch(name, `/${name}`)
    }, 1000)

    if (autoFetch)
        onMounted(fetch)

    const refresh = (id) => {
        do_fetch(name, `/${name}/${id}`)
    }

    return {fetch, [name]: local_data, data: local_data, refresh}
}
