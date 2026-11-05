<script setup>
import { computed, nextTick, ref, shallowRef, watch } from "vue"
import { RouterLink, useRoute, useRouter } from "vue-router"
import { NButton } from "naive-ui"

import AppIcon from "@/components/app/AppIcon.vue"
import SegmentedControl from "@/components/app/SegmentedControl.vue"
import AreaFormDialog from "@/components/area/AreaFormDialog.vue"
import BoxList from "@/components/box/BoxList.vue"
import AreaBubbles from "@/components/map/AreaBubbles.vue"
import BaseMap from "@/components/map/BaseMap.vue"
import BoxClusters from "@/components/map/BoxClusters.vue"
import MapFilters from "@/components/map/MapFilters.vue"
import MapPanelLayout from "@/components/map/MapPanelLayout.vue"
import PlannedBoxes from "@/components/map/PlannedBoxes.vue"
import {
  ACTIVE_STATUSES,
  boxRowDetail,
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
  filterBoxes,
  legendCounts,
  matchesSearch,
  seasonStateParams,
  useFilters,
} from "@/composables/filters.js"
import { byId } from "@/composables/labels.js"
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
const STATE_KEYS = ["planned", "to_check", "attention", "done"]
const STATISTICS_UNAVAILABLE = {
  shown: "Statistiky stavy budek nerozlišují.",
  unverified: "Statistiky neověřené budky nerozlišují.",
  checked: "Statistiky se počítají ze všech kontrol sezóny.",
}

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const { filters, update } = useFilters()
// The public map filters by the unit only
const { season, areas, statistics } = usePublicData(() =>
  auth.isManager ? filters.value.type : [],
)

// What a click on the map picked; the panel's rows act on it
const selectedAreaId = ref(null)
const selectedBoxId = ref(null)
const map = shallowRef(null)
const creatingArea = ref(false)
const view = ref("states")
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
const showsStatistics = computed(() => !showsBoxes.value && !showsStates.value)

const shownSeason = computed(() =>
  showsStatistics.value ? season.value : currentSeason(),
)

const types = computed(() => categories.value?.types ?? [])
const unitOptions = computed(() =>
  unitsOf(areas.value ?? []).map(unit => ({
    label: unit.abbreviation,
    value: unit.id,
  })),
)
// Newest first, so an older season is further down the list
const seasons = computed(() => statistics.value?.seasons ?? [])
const seasonIndex = computed(() => seasons.value.indexOf(season.value))
const stepSeason = step => (season.value = seasons.value[seasonIndex.value + step])

const inUnit = area =>
  filters.value.unit === null || area.administration_unit.id === filters.value.unit
const areaShown = area => inUnit(area) && matchesSearch(area.name, filters.value.search)

const areasById = computed(
  () => new Map((areas.value ?? []).map(area => [area.id, area])),
)
const areaNames = computed(
  () => new Map((areas.value ?? []).map(area => [area.id, area.name])),
)

const statisticsRows = computed(() =>
  (statistics.value?.areas ?? [])
    .filter(row => areaShown(row.area))
    .map(row => ({ ...row, ...describeFigures(row) })),
)
// The server filters by everything but the legend and the search
const searchedStateRows = computed(() =>
  areas.value && stateRows.value
    ? stateRows.value
        .map(row => ({ ...row, area: areasById.value.get(row.area_id) }))
        .filter(row => matchesSearch(row.area.name, filters.value.search))
    : [],
)
const stateCounts = computed(() =>
  Object.fromEntries(
    STATE_KEYS.map(key => [
      key,
      searchedStateRows.value.reduce((total, row) => total + row[key], 0),
    ]),
  ),
)
const statesRows = computed(() =>
  searchedStateRows.value
    .map(row => {
      const shown = Object.fromEntries(
        STATE_KEYS.map(key => [key, filters.value.shown.includes(key) ? row[key] : 0]),
      )
      return { ...row, ...shown, remaining: shown.to_check + shown.planned }
    })
    .filter(row => STATE_KEYS.some(key => row[key]))
    .sort((a, b) => a.area.name.localeCompare(b.area.name, "cs")),
)

const bubbles = computed(() => {
  if (!areas.value) return []
  return showsStates.value
    ? stateBubbles(statesRows.value, areas.value)
    : statisticsBubbles(statisticsRows.value, areas.value)
})

const unitBoxes = computed(() =>
  areas.value && mapBoxes.value
    ? mapBoxes.value.filter(box => inUnit(areasById.value.get(box.area_id)))
    : [],
)
const shownBoxes = computed(() =>
  filterBoxes(unitBoxes.value, filters.value, currentSeason()),
)
const boxGroups = computed(() => groupByArea(shownBoxes.value, areasById.value))
const unverifiedCount = computed(
  () =>
    unitBoxes.value.filter(
      box => !box.is_verified && ACTIVE_STATUSES.includes(box.status),
    ).length,
)
const legend = computed(() => {
  if (showsBoxes.value)
    return legendCounts(
      filterBoxes(unitBoxes.value, filters.value, currentSeason(), { legend: false }),
    )
  return showsStates.value ? stateCounts.value : null
})
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
    ? rows.reduce(
        (total, row) => total + STATE_KEYS.reduce((sum, key) => sum + row[key], 0),
        0,
      )
    : rows.reduce((total, row) => total + row.boxes, 0)
  return `${areaCountLabel(rows.length)}, ${boxCountLabel(boxTotal)}`
})
const totalFigures = computed(
  () => statistics.value && describeFigures(statistics.value.total),
)

watch(
  [
    showsStates,
    () => JSON.stringify(seasonStateParams(filters.value, currentSeason())),
  ],
  () => {
    if (!showsStates.value) return
    getSeasonStates(seasonStateParams(filters.value, currentSeason())).then(
      result => (stateRows.value = result),
      reportError,
    )
  },
  { immediate: true },
)

getCategories().then(result => (categories.value = result), reportError)

watch(
  showsBoxes,
  shows =>
    shows &&
    !mapBoxes.value &&
    listMapBoxes().then(result => (mapBoxes.value = result), reportError),
  { immediate: true },
)

const detailContext = computed(() => ({
  typesById: byId(types.value),
  occupantsById: byId(categories.value?.occupants ?? []),
  otherBatches: [],
}))
const detail = box => boxRowDetail(box, null, detailContext.value)

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
    <template #map="{ bottomInset, sheetStop }">
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
      <MapFilters
        :filters="filters"
        :units="unitOptions"
        :types="auth.isManager ? types : null"
        :states="auth.isManager"
        :unverified-count="auth.isManager ? unverifiedCount : null"
        :checked="auth.isManager"
        :unavailable="showsStatistics ? STATISTICS_UNAVAILABLE : {}"
        :search-placeholder="showsBoxes ? 'Hledat označení' : 'Hledat oblast'"
        :legend-counts="legend"
        :bottom-inset="bottomInset"
        :sheet-stop="sheetStop"
        @update="update"
      >
        <template v-if="auth.isManager" #mode>
          <SegmentedControl v-model="mode" :options="MODES" size="sm" />
        </template>
      </MapFilters>
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
    <div v-if="!showsBoxes" class="head">
      <SegmentedControl
        v-if="auth.isManager"
        v-model="view"
        :options="VIEWS"
        size="sm"
      />
      <template v-if="showsStatistics">
        <div v-if="totalFigures" class="totals">
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
        <div class="season-row">
          <div v-if="season" class="season-stepper">
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
          <RouterLink class="all-seasons small" :to="{ name: 'statistics' }">
            Všechny sezóny<AppIcon name="chev" />
          </RouterLink>
        </div>
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

.season-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  white-space: nowrap;
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

.all-seasons {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-weight: 700;
}

.all-seasons .icon {
  width: 14px;
  height: 14px;
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
