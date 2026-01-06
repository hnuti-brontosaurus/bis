import { computed, onMounted, toRef, unref } from "vue"
import { useMessage } from "naive-ui"
import { toRefs, useLocalStorage, useThrottleFn } from "@vueuse/core"
import axios from "axios"
import { mapping, propertyRef } from "@/contrib/composables/helpers.js"
import { handleAxiosError } from "@/contrib/composables/setup.js"

const storage = useLocalStorage(
  "connector",
  {
    recipes: {},
    menus: {},
    chefs: {},
    units: {},
    ingredients: {},
    recipe_difficulties: {},
    recipe_required_times: {},
    recipe_tags: {},
  },
  { mergeDefaults: true },
)

export const useConnector = (name, auto_fetch = true) => {
  const message = useMessage()
  const local_data = propertyRef(storage, name)

  const do_get = (name, url, ids = []) => {
    axios
      .get(url)
      .then(({ data }) => {
        let results = data.results
        if (!Array.isArray(results)) {
          local_data.value[data.id] = data
          return
        }
        results.forEach(row => (local_data.value[row.id] = row))
        ids = ids.concat(results.map(row => row.id))
        if (data.next) {
          do_get(name, data.next, ids)
        } else {
          ids = new Set(ids.map(id => id.toString()))
          for (const key of Object.keys(local_data.value)) {
            if (!ids.has(key)) {
              delete local_data.value[key]
            }
          }
        }
      })
      .catch(handleAxiosError(`Error fetching ${name}`))
  }

  const do_fetch = () => do_get(name, `/${name}/`)

  const fetch = useThrottleFn(() => do_fetch(), 60000)

  const refresh = id => do_get(name, `/${name}/${id}/`)

  if (auto_fetch === true) do_fetch()
  else if (auto_fetch) refresh(auto_fetch)

  const options = computed(() =>
    Object.values(local_data.value).map(_ => ({ label: _.name, value: _.id })),
  )

  const id_mapping = item =>
    mapping(
      () => item.value.id,
      value => (item.value = local_data.value[value]),
    )

  const mapNewFiles = ([key, value]) => [key, value?.base64data || value]
  const removeUploadedImages = ([key, value]) =>
    !(value?.small && value?.medium && value?.large && value?.original)

  const normalizeNested = ([key, value]) => [
    key,
    Array.isArray(value)
      ? value.map(_ => (_?.constructor === Object ? normalizePayload(_) : _))
      : value?.constructor === Object
        ? normalizePayload(value)
        : value,
  ]

  const normalizePayload = data => {
    return Object.fromEntries(
      Object.entries(data).map(mapNewFiles).map(normalizeNested),
    )
  }

  const normalizeIds = item => {
    if (name === "recipes") {
      if (item?.chef?.id) item.chef = item.chef.id
      if (item?.difficulty?.id) item.difficulty = item.difficulty.id
      if (item?.required_time?.id) item.required_time = item.required_time.id
      item?.ingredients?.map(_ => {
        if (_?.ingredient.id) _.ingredient = _.ingredient.id
        if (_?.unit.id) _.unit = _.unit.id
      })
      if (item?.tags?.length) item.tags = item.tags.map(_ => _?.id)
      item?.ingredients?.forEach((item, i) => (item.order = i))
      item?.tips?.forEach((item, i) => (item.order = i))
      item?.steps?.forEach((item, i) => (item.order = i))
    }
    return item
  }

  const upsert = item => {
    console.log(item.id)
    const url = `/${name}/` + (item.id ? item.id + "/" : "")
    const method = item.id ? "patch" : "post"
    console.log(item)
    item = JSON.parse(JSON.stringify(item))
    console.log(item)
    item = normalizeIds(item)
    item = normalizePayload(item)
    console.log(item)
    return axios[method](url, item).then(
      ({ data }) => (local_data.value[data.id] = data),
    )
  }

  return {
    fetch,
    [name]: local_data,
    data: local_data,
    refresh,
    do_fetch,
    options,
    id_mapping,
    upsert,
  }
}

export const {
  recipes,
  menus,
  chefs,
  units,
  ingredients,
  recipe_difficulties,
  recipe_required_times,
  recipe_tags,
} = toRefs(storage)

export const dataOptions = collection =>
  computed(() =>
    Object.values(collection.value).map(_ => ({ label: _.name, value: _.id })),
  )

export const dataIdMapping = (collection, item) =>
  mapping(
    () => item.value?.id,
    value => (item.value = collection.value[value]),
  )
