<script setup>
import { computed, nextTick, ref, shallowRef, watch } from "vue"
import { RouterLink, useRoute, useRouter } from "vue-router"
import { NButton, NPopselect, NSelect } from "naive-ui"

import AppIcon from "@/components/app/AppIcon.vue"
import SegmentedControl from "@/components/app/SegmentedControl.vue"
import AreaFormDialog from "@/components/area/AreaFormDialog.vue"
import BoxFilters from "@/components/box/BoxFilters.vue"
import BoxList from "@/components/box/BoxList.vue"
import AreaBubbles from "@/components/map/AreaBubbles.vue"
import BaseMap from "@/components/map/BaseMap.vue"
import BoxClusters from "@/components/map/BoxClusters.vue"
import MapLegend from "@/components/map/MapLegend.vue"
import MapPanelLayout from "@/components/map/MapPanelLayout.vue"
import PlannedBoxes from "@/components/map/PlannedBoxes.vue"
import {
  ACTIVE_STATUSES,
  boxRowDetail,
  defaultFilters,
  filterBoxes,
  groupByArea,
  markerState,
} from "@/composables/areaBoxes.js"
import {
  areaCountLabel,
  boxCountLabel,
  currentSeason,
  formatNumber,
  seasonLabel,
} from "@/composables/czech.js"
import {
  byId,
  categoryOptions,
  SEASON_STATE_LABELS,
  SEASON_STATE_OPTIONS,
} from "@/composables/labels.js"
import {
  describeFigures,
  stateBubbles,
  statisticsBubbles,
  unitsOf,
} from "@/composables/statistics.js"
import { usePublicData } from "@/composables/usePublicData.js"
import { useAuthStore } from "@/data/auth.js"
import { reportError } from "@/data/errors.js"
import { getCategories, getSeasonStates, listMapBoxes } from "@/data/manage.js"

const MODES = [
  { value: "areas", label: "Oblasti" },
  { value: "boxes", label: "Budky" },
]
const VIEWS = [
  { value: "states", label: "Stav budek" },
  { value: "statistics", label: "Statistiky" },
]
// Planned boxes are too rare for a column of their own
const STATE_COLUMNS = [
  { key: "remaining", label: "Zbývá" },
  { key: "attention", label: "K opravě" },
  { key: "done", label: "Hotovo" },
]
const TOTAL_LABELS = { remaining: "zbývá", attention: "k opravě", done: "hotovo" }

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const { season, areas, statistics } = usePublicData()

const unitId = ref(null)
// What a click on the map picked; the panel's rows act on it
const selectedAreaId = ref(null)
const selectedBoxId = ref(null)
const map = shallowRef(null)
const creatingArea = ref(false)
const view = ref("states")
const filters = ref({ state: [], type: [], unverified: false })
const boxFilters = ref(defaultFilters())
const categories = shallowRef(null)
const stateRows = shallowRef(null)
const mapBoxes = shallowRef(null)

// Box coordinates are for managers only
const mode = computed({
  get: () => (auth.isManager && route.query.mode === "boxes" ? "boxes" : "areas"),
  set: value =>
    router.replace({
      query: { ...route.query, mode: value === "boxes" ? value : undefined },
    }),
})
const showsBoxes = computed(() => mode.value === "boxes")
// Season states are live, so they belong to the current season only
const showsStates = computed(
  () => auth.isManager && !showsBoxes.value && view.value === "states",
)

const shownSeason = computed(() =>
  showsStates.value || showsBoxes.value ? currentSeason() : season.value,
)

const types = computed(() => categories.value?.types ?? [])
const unitOptions = computed(() =>
  unitsOf(areas.value ?? []).map(unit => ({ label: unit.name, value: unit.id })),
)
// Newest first, so an older season is further down the list
const seasons = computed(() => statistics.value?.seasons ?? [])
const seasonIndex = computed(() => seasons.value.indexOf(season.value))
const stepSeason = step => (season.value = seasons.value[seasonIndex.value + step])
const typeOptions = computed(() => categoryOptions(types.value))

const inUnit = area =>
  unitId.value === null || area.administration_unit.id === unitId.value

const areasById = computed(
  () => new Map((areas.value ?? []).map(area => [area.id, area])),
)
const areaNames = computed(
  () => new Map((areas.value ?? []).map(area => [area.id, area.name])),
)

const statisticsRows = computed(() =>
  (statistics.value?.areas ?? [])
    .filter(row => inUnit(row.area))
    .map(row => ({ ...row, ...describeFigures(row) })),
)
// The server filters by unit already
const statesRows = computed(() =>
  areas.value && stateRows.value
    ? stateRows.value
        .map(row => ({
          ...row,
          remaining: row.to_check + row.planned,
          area: areasById.value.get(row.area_id),
        }))
        .sort((a, b) => a.area.name.localeCompare(b.area.name, "cs"))
    : [],
)

const bubbles = computed(() => {
  if (!areas.value) return []
  return showsStates.value
    ? stateBubbles(statesRows.value, areas.value)
    : statisticsBubbles(statisticsRows.value, areas.value)
})

const stateTotals = computed(() =>
  Object.fromEntries(
    STATE_COLUMNS.map(({ key }) => [
      key,
      statesRows.value.reduce((total, row) => total + row[key], 0),
    ]),
  ),
)
const unitBoxes = computed(() =>
  areas.value && mapBoxes.value
    ? mapBoxes.value.filter(box => inUnit(areasById.value.get(box.area_id)))
    : [],
)
const shownBoxes = computed(() =>
  filterBoxes(unitBoxes.value, boxFilters.value, currentSeason()),
)
const boxGroups = computed(() => groupByArea(shownBoxes.value, areasById.value))
const unverifiedCount = computed(
  () =>
    unitBoxes.value.filter(
      box => !box.is_verified && ACTIVE_STATUSES.includes(box.status),
    ).length,
)
const markerBoxes = computed(() =>
  showsBoxes.value
    ? shownBoxes.value
        .filter(box => box.status !== "planned")
        .map(box => ({ ...box, state: markerState(box, null) }))
    : [],
)
const plannedBoxes = computed(() =>
  showsBoxes.value ? shownBoxes.value.filter(box => box.status === "planned") : [],
)

const heading = computed(() => {
  if (showsBoxes.value) return boxCountLabel(shownBoxes.value.length)
  const rows = showsStates.value ? statesRows.value : statisticsRows.value
  const boxTotal = showsStates.value
    ? Object.values(stateTotals.value).reduce((total, count) => total + count, 0)
    : rows.reduce((total, row) => total + row.boxes, 0)
  return `${areaCountLabel(rows.length)}, ${boxCountLabel(boxTotal)}`
})
const totalFigures = computed(
  () => statistics.value && describeFigures(statistics.value.total),
)

const filterParams = computed(() => ({
  season_state: filters.value.state,
  type: filters.value.type,
  administration_unit: unitId.value ?? undefined,
  is_verified: filters.value.unverified ? false : undefined,
}))

watch(
  [showsStates, filterParams],
  () => {
    if (!showsStates.value) return
    getSeasonStates(filterParams.value).then(
      result => (stateRows.value = result),
      reportError,
    )
  },
  { immediate: true },
)

watch(
  () => auth.isManager,
  isManager => isManager && getCategories().then(result => (categories.value = result)),
  { immediate: true },
)

watch(
  showsBoxes,
  shows =>
    shows &&
    !mapBoxes.value &&
    listMapBoxes().then(result => (mapBoxes.value = result), reportError),
  { immediate: true },
)

const detail = box =>
  boxRowDetail(box, null, {
    typesById: byId(types.value),
    occupantsById: byId(categories.value?.occupants ?? []),
    otherBatches: [],
  })

const canManage = auth.canManage

const onAreaCreated = area => router.push({ name: "area", params: { id: area.id } })

const scrollToRow = async selector => {
  await nextTick()
  document.querySelector(selector)?.scrollIntoView({ block: "nearest" })
}

// A second click on a marker opens it; the area page is for managers only
const selectArea = id => {
  if (id === selectedAreaId.value && auth.isManager)
    router.push({ name: "area", params: { id } })
  selectedAreaId.value = id
  scrollToRow(`[data-area-row="${id}"]`)
}

const selectBox = id => {
  if (id === selectedBoxId.value) router.push({ name: "box", params: { id } })
  selectedBoxId.value = id
  scrollToRow(`[data-box-row="${id}"]`)
}

const focusArea = areaId => {
  selectedAreaId.value = areaId
  const area = areasById.value.get(areaId)
  if (area.marker) map.value.flyTo({ center: area.marker.coordinates, zoom: 11 })
}

const focusBox = box => {
  selectedBoxId.value = box.id
  map.value.easeTo({
    center: box.location.coordinates,
    zoom: Math.max(map.value.getZoom(), 16),
  })
}
</script>

<template>
  <MapPanelLayout>
    <template #map="{ bottomInset }">
      <BaseMap :bottom-inset="bottomInset" @ready="map = $event">
        <AreaBubbles
          v-if="!showsBoxes"
          :areas="bubbles"
          :selected-id="selectedAreaId"
          @select="selectArea"
        />
        <template v-else>
          <PlannedBoxes :boxes="plannedBoxes" />
          <BoxClusters
            :boxes="markerBoxes"
            :selected-id="selectedBoxId"
            :area-names="areaNames"
            @select="selectBox"
          />
        </template>
      </BaseMap>
    </template>
    <template #summary>
      <div class="summary">
        <div class="row title-row">
          <div class="grow">
            <p v-if="shownSeason" class="eyebrow">
              Sezóna {{ seasonLabel(shownSeason) }}
            </p>
            <h2 data-testid="areas-summary">{{ heading }}</h2>
          </div>
          <n-button
            v-if="auth.me?.is_budkar"
            size="small"
            quaternary
            @click="creatingArea = true"
          >
            <template #icon><AppIcon name="plus" /></template>
            <span class="hide-sm">Nová oblast</span>
          </n-button>
        </div>
      </div>
    </template>
    <div class="head">
      <SegmentedControl v-if="auth.isManager" v-model="mode" :options="MODES" />
      <template v-if="showsBoxes">
        <n-select
          v-model:value="unitId"
          :options="unitOptions"
          size="small"
          placeholder="Všechny jednotky"
          filterable
          clearable
        />
        <BoxFilters
          v-model="boxFilters"
          :types="types"
          :unverified-count="unverifiedCount"
        />
        <MapLegend />
      </template>
      <template v-else>
        <SegmentedControl
          v-if="auth.isManager"
          v-model="view"
          :options="VIEWS"
          size="sm"
        />
        <div v-if="showsStates" class="totals three" data-testid="state-totals">
          <div v-for="column in STATE_COLUMNS" :key="column.key">
            <b class="num">{{ formatNumber(stateTotals[column.key]) }}</b>
            <span>{{ TOTAL_LABELS[column.key] }}</span>
          </div>
        </div>
        <div v-else-if="totalFigures" class="totals">
          <div>
            <b class="num">{{ formatNumber(statistics.total.cleaned) }}</b>
            <span>vyčištěno</span>
          </div>
          <div>
            <b class="num">{{ totalFigures.coverageLabel }}</b>
            <span>z budek</span>
          </div>
          <div>
            <b class="num">{{ totalFigures.occupancyLabel }}</b>
            <span>obsazeno</span>
          </div>
          <div>
            <b class="num">{{ totalFigures.previousOccupancyLabel }}</b>
            <span>obsazeno loni</span>
          </div>
        </div>
        <div class="filters" :class="{ single: showsStates }">
          <n-select
            v-model:value="unitId"
            :options="unitOptions"
            size="small"
            placeholder="Všechny jednotky"
            filterable
            clearable
          />
          <div v-if="!showsStates && season" class="season-stepper">
            <n-button
              size="small"
              quaternary
              aria-label="Starší sezóna"
              :disabled="seasonIndex === seasons.length - 1"
              @click="stepSeason(1)"
            >
              <template #icon><AppIcon name="chevl" /></template>
            </n-button>
            <span>Sezóna {{ seasonLabel(season) }}</span>
            <n-button
              size="small"
              quaternary
              aria-label="Novější sezóna"
              :disabled="seasonIndex <= 0"
              @click="stepSeason(-1)"
            >
              <template #icon><AppIcon name="chev" /></template>
            </n-button>
          </div>
        </div>
        <div v-if="showsStates" class="chips">
          <n-popselect
            v-model:value="filters.state"
            :options="SEASON_STATE_OPTIONS"
            multiple
            trigger="click"
          >
            <button type="button" class="chip" :class="{ on: filters.state.length }">
              <AppIcon name="filter" />{{
                filters.state.length === 1
                  ? SEASON_STATE_LABELS[filters.state[0]]
                  : `Stav${filters.state.length ? ` ${filters.state.length}` : ""}`
              }}
            </button>
          </n-popselect>
          <n-popselect
            v-model:value="filters.type"
            :options="typeOptions"
            multiple
            trigger="click"
            scrollable
          >
            <button type="button" class="chip" :class="{ on: filters.type.length }">
              <AppIcon name="filter" />Typ<template v-if="filters.type.length">
                {{ filters.type.length }}</template
              >
            </button>
          </n-popselect>
          <button
            type="button"
            class="chip"
            :class="{ on: filters.unverified }"
            @click="filters.unverified = !filters.unverified"
          >
            Neověřené
          </button>
        </div>
        <MapLegend v-if="showsStates" />
      </template>
    </div>
    <p v-if="showsBoxes && !mapBoxes" class="muted loading">Načítám budky…</p>
    <BoxList
      v-else-if="showsBoxes"
      :groups="boxGroups"
      :selected-id="selectedBoxId"
      :detail="detail"
      :state-of="box => markerState(box, null)"
      @focus="focusBox"
    />
    <template v-else>
      <div class="scroll-x">
        <table v-if="showsStates" class="tbl" data-testid="season-states">
          <thead>
            <tr>
              <th class="first">Oblast</th>
              <th v-for="column in STATE_COLUMNS" :key="column.key" class="r">
                {{ column.label }}
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="row in statesRows"
              :key="row.area_id"
              :data-area-row="row.area_id"
              :class="{ selected: selectedAreaId === row.area_id }"
              @click="focusArea(row.area_id)"
            >
              <td class="first">
                <RouterLink
                  :to="{ name: 'area', params: { id: row.area_id } }"
                  @click.stop
                >
                  <b>{{ row.area.name }}</b>
                </RouterLink>
                <div class="small muted">
                  {{ row.area.administration_unit.abbreviation }}
                </div>
              </td>
              <td
                v-for="column in STATE_COLUMNS"
                :key="column.key"
                class="r num"
                :class="[column.key, { muted: !row[column.key] }]"
              >
                {{ formatNumber(row[column.key]) }}
              </td>
            </tr>
          </tbody>
        </table>
        <table v-else class="tbl" data-testid="statistics">
          <thead>
            <tr>
              <th class="first">Oblast</th>
              <th class="r">Budek</th>
              <th class="r">Vyčištěno</th>
              <th class="r">Obsaz.</th>
              <th class="r">Loni</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="row in statisticsRows"
              :key="row.area.id"
              :data-area-row="row.area.id"
              :class="{ selected: selectedAreaId === row.area.id }"
              @click="focusArea(row.area.id)"
            >
              <td class="first">
                <RouterLink
                  v-if="canManage(row.area.id)"
                  :to="{ name: 'area', params: { id: row.area.id } }"
                  @click.stop
                >
                  <b>{{ row.area.name }}</b>
                </RouterLink>
                <b v-else>{{ row.area.name }}</b>
                <div class="small muted">
                  {{ row.area.administration_unit.abbreviation }}
                </div>
              </td>
              <td class="r num">{{ formatNumber(row.boxes) }}</td>
              <td class="r num">
                {{ row.coverageLabel }}
                <span class="bar"
                  ><i :style="{ width: `${(row.coverage ?? 0) * 100}%` }"
                /></span>
              </td>
              <td class="r num">{{ row.occupancyLabel }}</td>
              <td class="r num muted">{{ row.previousOccupancyLabel }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <p v-if="showsStates" class="small muted footnote">
        Letošní stav včetně kontrol, které čekají na potvrzení. K opravě jsou
        nenalezené, poškozené, nevyčištěné a příliš blízko visící budky. Zbývají i
        plánované budky.
      </p>
      <p v-else class="small muted footnote">
        Jen potvrzené kontroly. Obsazenost se počítá z budek, do kterých někdo opravdu
        nahlédl. Sezóna začíná 1. července. Bubliny ukazují podíl hotových budek a těch
        k opravě, letos i s kontrolami čekajícími na potvrzení.
      </p>
    </template>
    <AreaFormDialog v-model:show="creatingArea" @saved="onAreaCreated" />
  </MapPanelLayout>
</template>

<style scoped>
.summary {
  padding: 18px 20px 12px;
}

.summary h2 {
  margin-top: 4px;
}

.head {
  padding: 0 20px 14px;
  display: grid;
  gap: 12px;
  border-bottom: 1px solid var(--line);
}

.totals {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 8px;
}

.totals.three {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.totals div {
  display: grid;
  gap: 2px;
}

.totals b {
  font-size: 24px;
  font-weight: 800;
  line-height: 1.05;
}

.totals span {
  font-size: 12.5px;
  color: var(--muted);
}

.filters {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 8px;
}

.filters.single {
  grid-template-columns: 1fr;
}

.season-stepper {
  display: flex;
  align-items: center;
  gap: 2px;
  font-size: 14px;
  font-weight: 700;
  white-space: nowrap;
}

.tbl .first {
  padding-left: 20px;
}

.tbl tbody tr {
  cursor: pointer;
}

.tbl tr.selected td {
  background: var(--primary-soft);
}

.tbl td.attention:not(.muted) {
  color: var(--warn);
  font-weight: 800;
}

.bar {
  display: block;
  width: 46px;
  height: 6px;
  border-radius: 9px;
  background: var(--surface-2);
  margin: 4px 0 0 auto;
  overflow: hidden;
}

.bar i {
  display: block;
  height: 100%;
  background: var(--primary);
}

.footnote {
  padding: 12px 20px;
}

.title-row {
  align-items: flex-start;
  flex-wrap: nowrap;
}

.grow {
  flex: 1;
  min-width: 0;
}

.loading {
  padding: 14px 20px;
}

@media (max-width: 720px) {
  .summary {
    padding: 0 16px 10px;
  }

  .head {
    padding: 0 16px 12px;
  }

  .tbl .first {
    padding-left: 16px;
  }
}
</style>
