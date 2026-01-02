import { NFlex } from "naive-ui"
import { h, onMounted } from "vue"
import { useLocalStorage, useThrottleFn } from "@vueuse/core"
import axios from "axios"
import { useErrorHandler } from "@/contrib/composables/errorHandler.js"

const data = useLocalStorage("segmentations", {})
let fetch

export function useSegmentations() {
  const { handleAxiosError } = useErrorHandler()
  const columns = [
    { type: "selection", fixed: "left" },
    { title: "Audience", key: "audience_name", sorter: "default" },
    { title: "ID", key: "segmentation_id", sorter: "default" },
    { title: "Name", key: "segmentation_name", sorter: "default" },
    {
      title: "segments",
      key: "segments",
      render(row) {
        return h(NFlex, { vertical: true }, () =>
          row.segments?.map(segment => h("div", {}, segment.segment_name)),
        )
      },
    },
    {
      title: "Exists in exponea?",
      key: "exists_in_exponea",
      sorter: (a, b) =>
        a.exists_in_exponea === b.exists_in_exponea ? 0 : a.exists_in_exponea ? 1 : -1,
    },
    { title: "Actions count", key: "actions_count", sorter: "default" },
  ]

  fetch ??= useThrottleFn(() => {
    axios
      .get("/segmentations")
      .then(result => (data.value = result.data))
      .catch(handleAxiosError("Failed to fetch segmentations"))
  }, 1000)

  const _upsert = (url, segmentation) =>
    axios
      .post(url, segmentation)
      .then(result => Object.assign(segmentation, result.data))
      .then(fetch)

  const upsert = segmentation => _upsert("/segmentations", segmentation)
  const detail = segmentation => _upsert("/segmentations/detail", segmentation)

  onMounted(fetch)

  return { columns, upsert, detail, data }
}
