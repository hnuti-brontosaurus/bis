import { client, fetchAll } from "@/data/client.js"

/**
 * @typedef {Object} PublicArea
 * @property {number} id
 * @property {string} name
 * @property {{ id: number, name: string }} administration_unit
 * @property {{ type: "Point", coordinates: [number, number] } | null} marker
 *   centroid of the area's boxes in use; null for an area without any
 * @property {number} box_count
 */

/** @returns {Promise<PublicArea[]>} */
export const listPublicAreas = () => fetchAll("/public/areas/")

/**
 * @typedef {Object} PublicRegion
 * @property {number | "abroad"} id "abroad" for the boxes outside every region
 * @property {string} name
 * @property {{ type: "Point", coordinates: [number, number] }} marker
 *   a point inside the region, never one of its boxes
 * @property {{ type: "Polygon", coordinates: number[][][] } | null} outline
 *   simplified; null abroad
 * @property {number} box_count boxes in use
 */

let regions = null
/** @returns {Promise<PublicRegion[]>} fetched once: the outlines never change */
export const listPublicRegions = () =>
  (regions ??= client.get("/public/regions/").then(({ data }) => data))

/**
 * @typedef {Object} SeasonFigures
 * @property {number} boxes boxes in the season
 * @property {number} cleaned
 * @property {number} inspected
 * @property {number} occupied
 * @property {number} bird_occupied
 * @property {number} previous_inspected the season before
 * @property {number} previous_occupied
 * @property {number} done this season's live season states, a past one's checks
 * @property {number} attention
 *
 * @typedef {SeasonFigures & { area: { id: number, name: string,
 *   administration_unit: { id: number, name: string } } }} AreaSeasonFigures
 *
 * Mirrors `season_statistics` in backend/nest_boxes/statistics.py.
 * @typedef {Object} Statistics
 * @property {number} season
 * @property {number[]} seasons every season since the first check, newest first
 * @property {AreaSeasonFigures[]} areas
 * @property {SeasonFigures} total
 */

/**
 * @param {number} [season] without one the server's default, see `default_season`
 * @param {number[]} [type] box type ids, all when empty
 * @returns {Promise<Statistics>}
 */
export const getStatistics = (season, type) =>
  client
    .get("/public/statistics/", { params: { season, type } })
    .then(({ data }) => data)

export const getSeasonStatistics = type =>
  client
    .get("/public/statistics/seasons/", { params: { type } })
    .then(({ data }) => data)

export const sendWantToHang = payload => client.post("/public/want_to_hang/", payload)
