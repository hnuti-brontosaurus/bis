import { computed, onMounted, ref, toRef } from "vue"
import { useMessage } from "naive-ui"
import {
  createSharedComposable,
  toRefs,
  useLocalStorage,
  useStorage,
  useThrottleFn,
} from "@vueuse/core"
import axios from "axios"
import { handleAxiosError } from "@/contrib/composables/setup.js"

const translations = useLocalStorage(
  "translations",
  {
    string_translations: {
      generic: {},
      cookbook: {
        common: {},
      },
    },
    model_translations: {},
  },
  { mergeDefaults: true },
)

export const _ = computed(() => {
  const data = {}

  Object.entries(translations.value.model_translations).forEach(
    ([model_name, model_data]) => {
      model_data.fields ??= {}
      model_data.fields.class = model_data.name
      model_data.fields.plural = model_data.name_plural || model_data.name
      data[model_name] = new Proxy(
        {},
        {
          get: (_, key) =>
            model_data.fields[key] ||
            translations.value.string_translations.cookbook.common[key] ||
            translations.value.string_translations.generic[key] ||
            `${model_name}.${key}`,
        },
      )
    },
  )
  Object.entries(translations.value.string_translations.cookbook ?? {}).forEach(
    ([group, items]) => {
      data[group] = new Proxy(
        {},
        {
          get: (_, key) =>
            items?.[key] ||
            translations.value.string_translations.cookbook.common[key] ||
            translations.value.string_translations.generic[key] ||
            `${group}.${key}`,
        },
      )
    },
  )

  return new Proxy(data, {
    get: (_, key) =>
      data[key] || new Proxy({}, { get: (_, subkey) => `${key}.${subkey}` }),
  })
})

export const useTranslations = createSharedComposable(() => {
  axios
    .get("/extras/translations/")
    .then(({ data }) => (translations.value = data))
    .catch(handleAxiosError("Failed to fetch translations"))
})

export const translatedKey =
  (prefix = "common") =>
  key => {
    return { key, label: _.value[prefix][key] }
  }
