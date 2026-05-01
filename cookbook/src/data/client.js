import axios from "axios"
import { ConcurrencyManager } from "@/contrib/composables/concurrencyManager.js"
import { getAuthToken } from "./auth.js"

// Cap simultaneous in-flight requests so a fan-out from one view (e.g.
// EditRecipeView preloading chefs/difficulties/tags/units/ingredients in
// parallel) doesn't overwhelm a single shared dev backend. Tune up if it
// becomes a bottleneck.
const MAX_CONCURRENT_REQUESTS = 5

const client = axios.create({ baseURL: "/api/cookbook" })
ConcurrencyManager(client, MAX_CONCURRENT_REQUESTS)

client.interceptors.request.use(config => {
  const token = getAuthToken()
  if (token) config.headers["Authorization"] = `Token ${token}`
  return config
})

export { client }

/**
 * Walk a paginated DRF list endpoint, returning all results.
 *
 * DRF returns absolute `next` URLs built from the request's Host header,
 * which can point to a different origin/port than the SPA (matters under
 * cypress where the test stack runs on a non-default port and the dev
 * stack might also be up). Strip scheme+host AND the axios baseURL prefix
 * so axios re-prepends the right one.
 */
const baseURL = client.defaults.baseURL ?? ""
const toRelative = url => {
  const noOrigin = url.replace(/^https?:\/\/[^/]+/, "")
  return baseURL && noOrigin.startsWith(baseURL)
    ? noOrigin.slice(baseURL.length)
    : noOrigin
}
export const fetchAll = async url => {
  const out = []
  let next = url
  while (next) {
    const { data } = await client.get(toRelative(next))
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

/**
 * Build a default `{ list, get, save }` namespace for an entity that lives
 * at `${path}/`. Saves PATCH for existing rows, POST for new ones.
 */
export const crudApi = path => ({
  list: () => fetchAll(`${path}/`),
  get: id => client.get(`${path}/${id}/`).then(r => r.data),
  save: payload => upsert(path, payload),
})
