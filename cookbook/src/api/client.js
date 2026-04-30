import axios from "axios"
import { ConcurrencyManager } from "@/contrib/composables/concurrencyManager.js"
import { me } from "@/composables/auth.js"

const client = axios.create({ baseURL: "/api/cookbook" })
ConcurrencyManager(client, 5)

client.interceptors.request.use(config => {
  const token = me.value.user?.token
  if (token) config.headers["Authorization"] = `Token ${token}`
  return config
})

export { client }

/**
 * Walk a paginated DRF list endpoint, returning all results.
 */
export const fetchAll = async url => {
  const out = []
  let next = url
  while (next) {
    const { data } = await client.get(next)
    if (!Array.isArray(data.results)) return [data]
    out.push(...data.results)
    next = data.next
  }
  return out
}

/**
 * Unwrap {base64data} blobs the file-input component nests around new
 * uploads. Existing thumbnail dicts (read-only) pass through unchanged —
 * DRF's ImageField ignores them on PATCH.
 */
const stripFileWrappers = payload => {
  const out = {}
  for (const [k, v] of Object.entries(payload)) {
    out[k] = v && typeof v === "object" && "base64data" in v ? v.base64data : v
  }
  return out
}

export const upsert = async (basePath, payload) => {
  const id = payload.id
  const url = `${basePath}/${id ? `${id}/` : ""}`
  const method = id ? "patch" : "post"
  const { data } = await client[method](url, stripFileWrappers(payload))
  return data
}
