import { useLocalStorage, useThrottleFn } from "@vueuse/core"
import axios from "axios"
import { useErrorHandler } from "@/contrib/composables/errorHandler.js"
import { useMessage } from "naive-ui"
import { onMounted } from "vue"
let fetch

const configs = {
  nba_config: useLocalStorage(
    "nba_config",
    {
      channel_nba_limit: {},
      channel_sorting: {},
      audience_limit: {},
      digi_channels: {},
    },
    { mergeDefaults: true },
  ),
  contact_policy_config: useLocalStorage(
    "contact_policy_config",
    {
      cp_groups: [],
      group_exclusion: {},
      single_aggregated_exclusion: {},
      group_aggregated_exclusion: {},
    },
    { mergeDefaults: true },
  ),
}

export const useConfigs = () => {
  const { handleAxiosError } = useErrorHandler()
  const message = useMessage()

  fetch ??= useThrottleFn(() => {
    axios
      .get("/configs")
      .then(({ data }) => {
        configs.nba_config.value = data.nba_config
        configs.contact_policy_config.value = data.contact_policy_config
      })
      .catch(handleAxiosError("Failed to fetch configs"))
  }, 1000)

  const save_config = name =>
    axios
      .post(`/configs/${name}`, configs[name].value)
      .then(() => message.success(`Saved ${name}`))
      .catch(handleAxiosError(`Failed to save ${name}`))

  onMounted(fetch)

  return { ...configs, save_config, fetch }
}
