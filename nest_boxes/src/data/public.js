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

/** @returns {Promise<Statistics>} */
export const getStatistics = season =>
  client.get("/public/statistics/", { params: { season } }).then(({ data }) => data)

export const sendWantToHang = payload => client.post("/public/want_to_hang/", payload)
