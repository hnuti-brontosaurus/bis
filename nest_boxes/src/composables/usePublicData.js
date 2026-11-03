import { ref, shallowRef, watch } from "vue"

import { currentSeason } from "@/composables/czech.js"
import { reportError } from "@/data/errors.js"
import { getStatistics, listPublicAreas } from "@/data/public.js"

export const usePublicData = () => {
  const season = ref(currentSeason())
  const areas = shallowRef(null)
  const statistics = shallowRef(null)

  listPublicAreas().then(result => (areas.value = result), reportError)

  watch(
    season,
    value =>
      getStatistics(value).then(result => (statistics.value = result), reportError),
    { immediate: true },
  )

  return { season, areas, statistics }
}
