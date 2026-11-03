import { ref, shallowRef } from "vue"

import { reportError } from "@/data/errors.js"

/**
 * Runs `load` now and again on `reload()`; `data` keeps the last result and
 * `failed` says the first load never arrived, so a page can stop saying "Načítám".
 */
export const useLoad = load => {
  const data = shallowRef(null)
  const failed = ref(false)

  const reload = () =>
    load().then(
      result => (data.value = result),
      error => {
        failed.value = data.value === null
        reportError(error)
      },
    )

  const loaded = reload()
  return { data, failed, reload, loaded }
}
