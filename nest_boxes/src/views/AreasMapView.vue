<script setup>
import { computed, nextTick, ref, shallowRef } from "vue"
import { RouterLink, useRouter } from "vue-router"
import { NSelect } from "naive-ui"

import AreaBubbles from "@/components/map/AreaBubbles.vue"
import BaseMap from "@/components/map/BaseMap.vue"
import MapPanelLayout from "@/components/map/MapPanelLayout.vue"
import {
  areaCountLabel,
  boxCountLabel,
  currentSeason,
  formatNumber,
  seasonLabel,
} from "@/composables/czech.js"
import { describeFigures, recentSeasons, unitsOf } from "@/composables/statistics.js"
import { usePublicData } from "@/composables/usePublicData.js"
import { useAuthStore } from "@/data/auth.js"

const SEASONS_SHOWN = 5

const router = useRouter()
const auth = useAuthStore()
const { season, areas, statistics } = usePublicData()

const unitId = ref(null)
const selectedId = ref(null)
const map = shallowRef(null)

const unitOptions = computed(() =>
  unitsOf(areas.value ?? []).map(unit => ({ label: unit.name, value: unit.id })),
)
const seasonOptions = recentSeasons(currentSeason(), SEASONS_SHOWN).map(value => ({
  label: `Sezóna ${seasonLabel(value)}`,
  value,
}))

const inUnit = area =>
  unitId.value === null || area.administration_unit.id === unitId.value

const shownAreas = computed(() => (areas.value ?? []).filter(inUnit))
const mappedAreas = computed(() => shownAreas.value.filter(area => area.marker))
const rows = computed(() =>
  (statistics.value?.areas ?? [])
    .filter(row => inUnit(row.area))
    .map(row => ({ ...row, ...describeFigures(row) })),
)
const totalFigures = computed(
  () => statistics.value && describeFigures(statistics.value.total),
)
const boxTotal = computed(() =>
  shownAreas.value.reduce((total, area) => total + area.box_count, 0),
)

const canManage = areaId =>
  auth.me?.is_budkar || auth.me?.managed_area_ids.includes(areaId)

const onBubble = area => {
  if (canManage(area.id)) router.push({ name: "area", params: { id: area.id } })
  else selectArea(area.id)
}

const selectArea = async areaId => {
  selectedId.value = areaId
  await nextTick()
  document
    .querySelector(`[data-area-row="${areaId}"]`)
    ?.scrollIntoView({ block: "nearest" })
}

const focusArea = areaId => {
  selectedId.value = areaId
  const area = areas.value.find(item => item.id === areaId)
  if (area.marker) map.value.flyTo({ center: area.marker.coordinates, zoom: 11 })
}
</script>

<template>
  <MapPanelLayout>
    <template #map="{ bottomInset }">
      <BaseMap :bottom-inset="bottomInset" @ready="map = $event">
        <AreaBubbles
          :areas="mappedAreas"
          :selected-id="selectedId"
          @select="onBubble"
        />
      </BaseMap>
    </template>
    <template #summary>
      <div class="summary">
        <p class="eyebrow">Sezóna {{ seasonLabel(season) }}</p>
        <h2 data-testid="areas-summary">
          {{ areaCountLabel(shownAreas.length) }}, {{ boxCountLabel(boxTotal) }}
        </h2>
      </div>
    </template>
    <div class="head">
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
      <div class="filters">
        <n-select
          v-model:value="unitId"
          :options="unitOptions"
          size="small"
          filterable
        />
        <n-select v-model:value="season" :options="seasonOptions" size="small" />
      </div>
    </div>
    <div class="scroll-x">
      <table class="tbl" data-testid="statistics">
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
            v-for="row in rows"
            :key="row.area.id"
            :data-area-row="row.area.id"
            :class="{ selected: row.area.id === selectedId }"
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
              <div class="small muted">{{ row.area.administration_unit.name }}</div>
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
    <p class="small muted footnote">
      Jen potvrzené kontroly. Obsazenost se počítá z budek, do kterých někdo opravdu
      nahlédl. Sezóna začíná 1. července.
    </p>
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

.filters {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 8px;
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

.bar {
  display: inline-block;
  width: 46px;
  height: 6px;
  border-radius: 9px;
  background: var(--surface-2);
  vertical-align: middle;
  margin-left: 6px;
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
