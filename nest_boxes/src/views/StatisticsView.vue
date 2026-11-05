<script setup>
import { computed, nextTick, ref, shallowRef, watch } from "vue"
import { RouterLink } from "vue-router"
import { NSelect } from "naive-ui"

import AppIcon from "@/components/app/AppIcon.vue"
import SegmentedControl from "@/components/app/SegmentedControl.vue"
import { formatNumber, percent, seasonLabel } from "@/composables/czech.js"
import { useFilters } from "@/composables/filters.js"
import { categoryOptions } from "@/composables/labels.js"
import { ratio, seasonTable, unitsOf } from "@/composables/statistics.js"
import { useAuthStore } from "@/data/auth.js"
import { reportError } from "@/data/errors.js"
import { getCategories } from "@/data/manage.js"
import { getSeasonStatistics } from "@/data/public.js"

const METRICS = [
  {
    value: "occupancy",
    label: "Obsazenost",
    show: figures => percent(figures.occupied, figures.inspected),
    share: figures => ratio(figures.occupied, figures.inspected),
    title: figures =>
      `obsazeno ${figures.occupied} z ${figures.inspected} prohlédnutých budek`,
  },
  {
    value: "cleaned",
    label: "Vyčištěno",
    show: figures => (figures.boxes ? formatNumber(figures.cleaned) : "–"),
    share: figures => ratio(figures.cleaned, figures.boxes),
    title: figures =>
      `vyčištěno ${figures.cleaned} z ${figures.boxes} budek (${percent(figures.cleaned, figures.boxes)})`,
  },
  {
    value: "boxes",
    label: "Budek",
    show: figures => (figures.boxes ? formatNumber(figures.boxes) : "–"),
    share: () => null,
    title: figures => `${figures.boxes} budek k čištění`,
  },
]

const auth = useAuthStore()
const metricKey = ref("occupancy")
// The map's unit and type, shared through the URL
const { filters, update } = useFilters()
const statistics = shallowRef(null)
const types = shallowRef([])
const scroller = ref(null)

const metric = computed(() => METRICS.find(item => item.value === metricKey.value))
// Oldest on the left, so a row reads as a trend
const seasons = computed(() => [...(statistics.value?.seasons ?? [])].reverse())
const chronological = figures => [...figures].reverse()

const unitOptions = computed(() =>
  unitsOf((statistics.value?.areas ?? []).map(row => row.area)).map(unit => ({
    label: unit.abbreviation,
    value: unit.id,
  })),
)
const typeOptions = computed(() => categoryOptions(types.value))

const table = computed(() =>
  seasonTable(
    (statistics.value?.areas ?? []).filter(
      row =>
        filters.value.unit === null ||
        row.area.administration_unit.id === filters.value.unit,
    ),
  ),
)

const cell = figures => ({
  text: metric.value.show(figures),
  title: metric.value.title(figures),
  style:
    metric.value.share(figures) === null
      ? null
      : {
          background: `color-mix(in srgb, var(--primary) ${Math.round(metric.value.share(figures) * 35)}%, transparent)`,
        },
})

getCategories().then(result => (types.value = result.types), reportError)

watch(
  () => filters.value.type.join(","),
  async () => {
    try {
      statistics.value = await getSeasonStatistics(filters.value.type)
      await nextTick()
      scroller.value?.scrollTo({ left: scroller.value.scrollWidth })
    } catch (error) {
      reportError(error)
    }
  },
  { immediate: true },
)
</script>

<template>
  <main class="page statistics-page">
    <div>
      <RouterLink class="small back" :to="{ name: 'areas' }">
        <AppIcon name="chevl" />Mapa budek
      </RouterLink>
      <h1>Statistiky po sezónách</h1>
      <p class="muted lead">
        Jen potvrzené kontroly. Obsazenost se počítá z budek, do kterých někdo opravdu
        nahlédl. Sezóna začíná 1. července.
      </p>
    </div>
    <div class="controls">
      <SegmentedControl v-model="metricKey" :options="METRICS" size="sm" />
      <n-select
        :value="filters.unit"
        :options="unitOptions"
        size="small"
        placeholder="Všechny jednotky"
        filterable
        clearable
        @update:value="update({ unit: $event })"
      />
      <n-select
        :value="filters.type"
        :options="typeOptions"
        size="small"
        placeholder="Všechny typy budek"
        multiple
        clearable
        max-tag-count="responsive"
        @update:value="update({ type: $event })"
      />
    </div>
    <p v-if="!statistics" class="muted">Načítám…</p>
    <p v-else-if="!table.units.length" class="muted">
      Žádné budky neodpovídají filtru.
    </p>
    <div v-else ref="scroller" class="scroll-x">
      <table class="tbl seasons" data-testid="season-statistics">
        <thead>
          <tr>
            <th class="first">Oblast</th>
            <th v-for="season in seasons" :key="season" class="r">
              {{ seasonLabel(season) }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr class="total">
            <td class="first">Celkem</td>
            <td
              v-for="(figures, index) in chronological(table.total)"
              :key="index"
              class="r num"
              :title="cell(figures).title"
              :style="cell(figures).style"
            >
              {{ cell(figures).text }}
            </td>
          </tr>
        </tbody>
        <tbody v-for="group in table.units" :key="group.unit.id">
          <tr class="unit">
            <td class="first">{{ group.unit.abbreviation }}</td>
            <td
              v-for="(figures, index) in chronological(group.seasons)"
              :key="index"
              class="r num"
              :title="cell(figures).title"
              :style="cell(figures).style"
            >
              {{ cell(figures).text }}
            </td>
          </tr>
          <tr v-for="row in group.areas" :key="row.area.id">
            <td class="first area">
              <RouterLink
                v-if="auth.isManager"
                :to="{ name: 'area', params: { id: row.area.id } }"
                >{{ row.area.name }}</RouterLink
              >
              <template v-else>{{ row.area.name }}</template>
            </td>
            <td
              v-for="(figures, index) in chronological(row.seasons)"
              :key="index"
              class="r num"
              :class="{ muted: cell(figures).text === '–' }"
              :title="cell(figures).title"
              :style="cell(figures).style"
            >
              {{ cell(figures).text }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </main>
</template>

<style scoped>
.statistics-page {
  max-width: 1400px;
}

.back {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  margin-bottom: 8px;
}

.back .icon {
  width: 14px;
  height: 14px;
}

.controls {
  display: grid;
  grid-template-columns: auto minmax(0, 260px) minmax(0, 320px);
  gap: 12px;
  align-items: center;
}

.seasons {
  width: auto;
  min-width: 100%;
}

.seasons th.r,
.seasons td.r {
  min-width: 68px;
}

.seasons .first {
  position: sticky;
  left: 0;
  z-index: 1;
  background: var(--bg);
  min-width: 200px;
  max-width: 260px;
}

.seasons tr.total td,
.seasons tr.unit td {
  font-weight: 800;
}

.seasons tr.total td {
  border-bottom: 1px solid var(--line-strong);
}

.seasons tr.unit td {
  padding-top: 18px;
}

.seasons tr.unit td.first {
  font-size: 13px;
  color: var(--primary-text);
}

.seasons td.area {
  padding-left: 20px;
}

@media (max-width: 720px) {
  .controls {
    grid-template-columns: minmax(0, 1fr);
  }

  .seasons .first {
    min-width: 140px;
  }
}
</style>
