import { ref, shallowRef, watch } from "vue"

import { reportError } from "@/data/errors.js"
import { getStatistics, listPublicAreas } from "@/data/public.js"

/** `season` starts null: the server picks the default, see `default_season`. */
export const usePublicData = () => {
  const season = ref(null)
  const areas = shallowRef(null)
  const statistics = shallowRef(null)

  listPublicAreas().then(result => (areas.value = result), reportError)

  const load = value =>
    getStatistics(value).then(result => {
      statistics.value = result
      season.value = result.season
    }, reportError)

  load()
  watch(season, value => value !== statistics.value.season && load(value))

  return { season, areas, statistics }
}
