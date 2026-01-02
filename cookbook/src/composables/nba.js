import { useStorage, useThrottleFn } from "@vueuse/core"
import axios from "axios"
import { useErrorHandler } from "@/contrib/composables/errorHandler.js"
import { onMounted } from "vue"

const calls = useStorage("nba_calls", {})
const form = useStorage("nba_form", {})
let fetch

export function useNBA() {
  const { handleAxiosError } = useErrorHandler()

  fetch ??= useThrottleFn(() => {
    axios
      .get("/nba/calls")
      .then(
        ({ data }) =>
          (calls.value = Object.fromEntries(data.map(item => [item.name, item]))),
      )
      .catch(handleAxiosError("Failed to fetch nba calls"))
  }, 1000)

  onMounted(fetch)

  const call = (url, data) =>
    axios.post(url, data, {
      headers: { "request-id": data.request_id },
    })

  const checkNBA = data => call("/nba/calculation", data)

  const checkEligibility = data => call("/nba/segmentations_check", data)

  const save = data => {
    calls.value[data.name] = data
    axios
      .post(`/nba/calls/${data.name}`, { data })
      .catch(handleAxiosError("Error saving call"))
  }

  const remove = name => {
    delete calls.value[name]
    axios.delete(`/nba/calls/${name}`).catch(handleAxiosError("Error deleting call"))
  }

  return { calls, form, checkNBA, save, checkEligibility, remove, fetch }
}
