import { computed, watch } from "vue"
import { useRoute, useRouter } from "vue-router"

import { seasonStart } from "@/composables/czech.js"

// A box's entry in the map legend: its season state, or "ended", which has none
export const LEGEND_KEYS = ["planned", "to_check", "attention", "done", "ended"]
// Ended boxes are history; the map starts without them.
const DEFAULT_SHOWN = LEGEND_KEYS.filter(key => key !== "ended")

export const CHECKED_OPTIONS = [
  { value: "this_season", label: "Letos zkontrolované" },
  { value: "before", label: "Naposledy před letoškem" },
  { value: "never", label: "Nikdy nezkontrolované" },
]

export const legendKey = box => box.season_state ?? "ended"

// Why a box needs attention, see SeasonStateFilter.problem
export const PROBLEM_KEYS = [
  "needs_repair",
  "needs_replacing",
  "taken_down",
  "missing",
  "moved",
  "not_cleaned",
]

const hasProblem = (box, problems) =>
  problems.includes(box.season_status) ||
  (problems.includes("moved") && box.should_be_moved) ||
  (problems.includes("not_cleaned") && box.season_cleaning === "not_cleaned")

export const defaultFilters = () => ({
  unit: null,
  type: [],
  shown: [...DEFAULT_SHOWN],
  problem: [],
  // true or false for only the verified or unverified boxes, null for all
  verified: null,
  checked: null,
  search: "",
})

const numbers = text => (text ? text.split(",").map(Number) : [])

/** The filters of the map and the area page, kept in the URL by these keys. */
export const parseFilters = query => ({
  unit: query.unit ? Number(query.unit) : null,
  type: numbers(query.type),
  shown:
    query.states === undefined
      ? [...DEFAULT_SHOWN]
      : query.states.split(",").filter(key => LEGEND_KEYS.includes(key)),
  problem: (query.problem ?? "").split(",").filter(key => PROBLEM_KEYS.includes(key)),
  verified: query.verified === undefined ? null : query.verified === "1",
  checked: CHECKED_OPTIONS.some(option => option.value === query.checked)
    ? query.checked
    : null,
  search: query.q ?? "",
})

export const isDefaultShown = shown =>
  shown.length === DEFAULT_SHOWN.length &&
  DEFAULT_SHOWN.every(key => shown.includes(key))

export const filterQuery = filters => ({
  unit: filters.unit ?? undefined,
  type: filters.type.length ? filters.type.join(",") : undefined,
  states: isDefaultShown(filters.shown)
    ? undefined
    : LEGEND_KEYS.filter(key => filters.shown.includes(key)).join(","),
  problem: filters.problem.length ? filters.problem.join(",") : undefined,
  verified: filters.verified === null ? undefined : filters.verified ? "1" : "0",
  checked: filters.checked ?? undefined,
  q: filters.search || undefined,
})

const FILTER_KEYS = Object.keys(filterQuery(defaultFilters()))

// What the last view showed, so stepping from the map to an area keeps it.
// Not the search: on the map it may be an area's name.
let remembered = {}

/**
 * The filters of the current route as a model: writes replace the URL's
 * query. A view opened without any filter in its URL starts from the ones
 * the previous view had.
 */
export const useFilters = () => {
  const route = useRoute()
  const router = useRouter()

  if (!FILTER_KEYS.some(key => key in route.query) && Object.keys(remembered).length)
    router.replace({ query: { ...route.query, ...remembered } })

  const filters = computed(() => parseFilters(route.query))
  watch(
    filters,
    value => {
      remembered = Object.fromEntries(
        Object.entries({ ...filterQuery(value), q: undefined }).filter(
          ([, item]) => item !== undefined,
        ),
      )
    },
    { immediate: true },
  )
  const update = patch =>
    router.replace({
      query: { ...route.query, ...filterQuery({ ...filters.value, ...patch }) },
    })
  return { filters, update }
}

const normalized = text => text.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase()

export const matchesSearch = (text, search) =>
  !search.trim() || normalized(text).includes(normalized(search.trim()))

/**
 * The client side of the boxes/ filters, so the list and the exports agree.
 * Without the legend's filter, for the legend's own counts.
 */
export const filterBoxes = (boxes, filters, season, { legend = true } = {}) => {
  const start = seasonStart(season)
  return boxes.filter(
    box =>
      (!legend || filters.shown.includes(legendKey(box))) &&
      (!filters.type.length || filters.type.includes(box.type_id)) &&
      (filters.verified === null || box.is_verified === filters.verified) &&
      (!filters.problem.length || hasProblem(box, filters.problem)) &&
      (filters.checked !== "this_season" ||
        (box.last_checked_on && box.last_checked_on >= start)) &&
      (filters.checked !== "before" ||
        (box.last_checked_on && box.last_checked_on < start)) &&
      (filters.checked !== "never" || !box.last_checked_on) &&
      matchesSearch(`${box.name} ${box.previous_names}`, filters.search),
  )
}

export const legendCounts = boxes => {
  const counts = Object.fromEntries(LEGEND_KEYS.map(key => [key, 0]))
  for (const box of boxes) counts[legendKey(box)] += 1
  return counts
}

const checkedParams = (checked, season) => {
  const start = seasonStart(season)
  return {
    ...(checked === "this_season" && { last_checked_after: start }),
    ...(checked === "before" && { last_checked_before: start }),
    ...(checked === "never" && { never_checked: true }),
  }
}

/** The filters but the legend as query parameters of areas/season_states/. */
export const seasonStateParams = (filters, season) => ({
  type: filters.type,
  administration_unit: filters.unit ?? undefined,
  problem: filters.problem,
  ...(filters.verified !== null && { is_verified: filters.verified }),
  ...checkedParams(filters.checked, season),
})

/** The same filters as query parameters of export.gpx / export.xlsx. */
export const exportParams = (filters, season) => ({
  state: filters.shown,
  type: filters.type,
  problem: filters.problem,
  ...(filters.verified !== null && { is_verified: filters.verified }),
  ...checkedParams(filters.checked, season),
})
