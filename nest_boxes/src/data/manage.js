import axios from "axios"

import { APP_PATH } from "@/config.js"
import { client, fetchAll } from "@/data/client.js"

const MAX_PAGE_SIZE = 200
const data = ({ data }) => data

let categories = null
/** categories/, fetched once: they change only with a deploy. */
export const getCategories = () =>
  (categories ??= client.get("/categories/").then(data))

export const listHelpArticles = () => client.get("/help_articles/").then(data)
export const updateHelpArticle = (slug, values) =>
  client.patch(`/help_articles/${slug}/`, values).then(data)
export const uploadHelpImage = (slug, image) =>
  client.post("/help_images/", { article: slug, image }).then(data)

// The BIS public API; every unit, for picking an area's.
export const listUnits = () =>
  axios
    .get("/api/web/administration_units/", { params: { page_size: MAX_PAGE_SIZE } })
    .then(({ data }) => data.results)

export const listAreas = () =>
  fetchAll("/areas/", { params: { page_size: MAX_PAGE_SIZE } })
export const getArea = id => client.get(`/areas/${id}/`).then(data)
export const createArea = values => client.post("/areas/", values).then(data)
export const updateArea = (id, values) =>
  client.patch(`/areas/${id}/`, values).then(data)

export const exportUrl = (areaId, format, params) => {
  const query = new URLSearchParams()
  Object.entries(params).forEach(([name, value]) =>
    [value].flat().forEach(item => query.append(name, item)),
  )
  return `${client.defaults.baseURL}/areas/${areaId}/export.${format}/?${query}`
}
export const importGpx = (areaId, payload) =>
  client.post(`/areas/${areaId}/import_gpx/`, payload).then(data)

/** [{ area_id, planned, to_check, attention, done }] of the boxes the filters pick. */
export const getSeasonStates = params =>
  client.get("/areas/season_states/", { params }).then(data)

export const listBoxes = params =>
  fetchAll("/boxes/", { params: { ...params, page_size: MAX_PAGE_SIZE } })
/** Every box of the manager's areas with just what the map and its list need. */
export const listMapBoxes = () => client.get("/boxes/map/").then(data)
export const getBox = id => client.get(`/boxes/${id}/`).then(data)
export const createBox = values => client.post("/boxes/", values).then(data)
export const updateBox = (id, values) =>
  client.patch(`/boxes/${id}/`, values).then(data)
export const getBoxHistory = id => client.get(`/boxes/${id}/history/`).then(data)
export const endBox = (id, values) =>
  client.post(`/boxes/${id}/end/`, values).then(data)
export const cancelBox = id => client.post(`/boxes/${id}/cancel/`).then(data)
export const confirmBox = id => client.post(`/boxes/${id}/confirm/`).then(data)
export const getBoxWarnings = params =>
  client
    .get("/boxes/warnings/", {
      params: {
        ...params,
        location: params.location && JSON.stringify(params.location),
      },
    })
    .then(data)

export const listChecks = params =>
  fetchAll("/checks/", { params: { ...params, page_size: MAX_PAGE_SIZE } })
export const createCheck = values => client.post("/checks/", values).then(data)
export const updateCheck = (id, values) =>
  client.patch(`/checks/${id}/`, values).then(data)
export const deleteCheck = id => client.delete(`/checks/${id}/`)
export const confirmCheck = id => client.post(`/checks/${id}/confirm/`).then(data)

/** Uploads a check's new photos after the existing ones and deletes the removed. */
export const saveCheckPhotos = async (check, { added, removed }) => {
  const kept = check.photos.filter(photo => !removed.includes(photo.id))
  await Promise.all(removed.map(id => client.delete(`/check_photos/${id}/`)))
  for (const [index, photo] of added.entries())
    await client.post("/check_photos/", {
      parent_id: check.id,
      photo,
      order: kept.length + index,
    })
}

export const listBatches = params =>
  fetchAll("/batches/", { params: { ...params, page_size: MAX_PAGE_SIZE } })
export const listOpenBatches = () => client.get("/batches/open/").then(data)
export const getBatch = id => client.get(`/batches/${id}/`).then(data)
export const createBatch = values => client.post("/batches/", values).then(data)
export const updateBatch = (id, values) =>
  client.patch(`/batches/${id}/`, values).then(data)
export const getSuggestedBoxes = areaId =>
  client.get("/batches/suggested/", { params: { area: areaId } }).then(data)
export const confirmBatch = id => client.post(`/batches/${id}/confirm/`).then(data)
export const closeBatch = id => client.post(`/batches/${id}/close/`).then(data)
export const addBatchBoxes = (id, boxIds) =>
  client.post(`/batches/${id}/add_boxes/`, { box_ids: boxIds }).then(data)
export const removeBatchBoxes = (id, boxIds) =>
  client.post(`/batches/${id}/remove_boxes/`, { box_ids: boxIds }).then(data)

export const linkUrl = token => `${window.location.origin}${APP_PATH}/d/${token}/`
