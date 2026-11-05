<script setup>
import { computed, nextTick, ref, shallowRef } from "vue"
import { RouterLink, useRoute, useRouter } from "vue-router"
import { NButton, useMessage } from "naive-ui"

import AppIcon from "@/components/app/AppIcon.vue"
import AreaFormDialog from "@/components/area/AreaFormDialog.vue"
import GpxImportDialog from "@/components/area/GpxImportDialog.vue"
import NewBatchDialog from "@/components/area/NewBatchDialog.vue"
import BatchLink from "@/components/batch/BatchLink.vue"
import BatchProgress from "@/components/batch/BatchProgress.vue"
import BoxFormDialog from "@/components/box/BoxFormDialog.vue"
import BoxList from "@/components/box/BoxList.vue"
import BaseMap from "@/components/map/BaseMap.vue"
import BoxMarkers from "@/components/map/BoxMarkers.vue"
import MapFilters from "@/components/map/MapFilters.vue"
import MapPanelLayout from "@/components/map/MapPanelLayout.vue"
import PlannedBoxes from "@/components/map/PlannedBoxes.vue"
import { boundsOf } from "@/components/map/geometry.js"
import {
  ACTIVE_STATUSES,
  boxExtras,
  markerState,
  withoutReplaced,
} from "@/composables/areaBoxes.js"
import { boxCountLabel, currentSeason } from "@/composables/czech.js"
import {
  exportParams as filterExportParams,
  filterBoxes,
  filterQuery,
  legendCounts,
  useFilters,
} from "@/composables/filters.js"
import { byId } from "@/composables/labels.js"
import { compareNames, latestChecks } from "@/composables/linkBoxes.js"
import { useLoad } from "@/composables/useLoad.js"
import { CZECHIA_BOUNDS } from "@/config.js"
import { useAuthStore } from "@/data/auth.js"
import {
  exportUrl,
  getArea,
  getCategories,
  listBatches,
  listChecks,
} from "@/data/manage.js"

const route = useRoute()
const router = useRouter()
const message = useMessage()
const auth = useAuthStore()
const season = currentSeason()
const areaId = Number(route.params.id)

const { data, reload } = useLoad(async () => {
  const [area, batches, checks, categories] = await Promise.all([
    getArea(areaId),
    listBatches({ area: areaId, is_open: true }),
    listChecks({ area: areaId, season }),
    getCategories(),
  ])
  return { area, batches, checks: latestChecks(checks), categories }
})

const map = shallowRef(null)
const selectedId = ref(null)
const { filters, update } = useFilters()
const dialogs = ref({ area: false, batch: false, plan: false, gpx: false })

const area = computed(() => data.value?.area)
const batches = computed(() => data.value?.batches ?? [])
const typesById = computed(() => byId(data.value?.categories.types ?? []))
const occupantsById = computed(() => byId(data.value?.categories.occupants ?? []))

const shown = computed(() =>
  area.value ? filterBoxes(area.value.boxes, filters.value, season) : [],
)
const sortedShown = computed(() => [...shown.value].sort(compareNames))
const legend = computed(() =>
  area.value
    ? legendCounts(
        filterBoxes(area.value.boxes, filters.value, season, { legend: false }),
      )
    : null,
)
const checkOf = box => data.value.checks.get(box.id)

const extras = box =>
  boxExtras(box, checkOf(box), {
    typesById: typesById.value,
    occupantsById: occupantsById.value,
    otherBatches: batches.value,
  })

const markerBoxes = computed(() =>
  withoutReplaced(shown.value, area.value.boxes)
    .filter(box => box.status !== "planned")
    .map(box => ({ ...box, state: markerState(box, null) })),
)
const plannedBoxes = computed(() => shown.value.filter(box => box.status === "planned"))

const bounds = computed(() => {
  const located = area.value.boxes.filter(box => ACTIVE_STATUSES.includes(box.status))
  return located.length ? boundsOf(located.map(box => box.location)) : CZECHIA_BOUNDS
})
const center = computed(
  () =>
    area.value.marker ??
    area.value.boxes[0]?.location ?? {
      type: "Point",
      coordinates: [15.5, 49.8],
    },
)

const summary = computed(() => boxCountLabel(shown.value.length))

const exportParams = computed(() => filterExportParams(filters.value, season))

const selectBox = async id => {
  if (id === selectedId.value) router.push({ name: "box", params: { id } })
  selectedId.value = id
  await nextTick()
  document.querySelector(`[data-box-row="${id}"]`)?.scrollIntoView({ block: "nearest" })
}

// A click on the selected row opens it, as a second click on its marker does
const focusBox = box => {
  if (box.id === selectedId.value)
    return router.push({ name: "box", params: { id: box.id } })
  selectedId.value = box.id
  map.value?.easeTo({
    center: box.location.coordinates,
    zoom: Math.max(map.value.getZoom(), 16),
  })
}

// A new batch opens on its link, where the manager sees and edits its boxes
const onBatchCreated = created => {
  auth.refresh()
  router.push({ name: "link", params: { token: created.token } })
}

const onPlanned = async box => {
  message.success(`Budka ${box.name} je naplánovaná.`)
  await reload()
}

const onImported = async count => {
  message.success(`Import je hotový, změněných budek: ${count}.`)
  await reload()
}
</script>

<template>
  <MapPanelLayout v-if="data">
    <template #map="{ bottomInset, sheetStop }">
      <BaseMap :bounds="bounds" :bottom-inset="bottomInset" @ready="map = $event">
        <PlannedBoxes :boxes="plannedBoxes" />
        <BoxMarkers
          :boxes="markerBoxes"
          :selected-id="selectedId"
          @select="selectBox"
        />
      </BaseMap>
      <MapFilters
        :filters="filters"
        :types="data.categories.types"
        verification
        search-placeholder="Hledat označení"
        :legend-counts="legend"
        :bottom-inset="bottomInset"
        :sheet-stop="sheetStop"
        @update="update"
      />
    </template>
    <template #summary>
      <div class="summary">
        <div class="row title-row">
          <div class="grow">
            <p class="eyebrow">{{ area.administration_unit.abbreviation }}</p>
            <h2>{{ area.name }}</h2>
          </div>
          <n-button size="small" quaternary @click="dialogs.area = true">
            <template #icon><AppIcon name="edit" /></template>
            <span class="hide-sm">Upravit</span>
          </n-button>
        </div>
        <p class="small muted only-sm">{{ summary }}</p>
      </div>
    </template>

    <section class="section batch" data-testid="batch-section">
      <template v-if="batches.length">
        <p class="eyebrow">Otevřené obchůzky</p>
        <div
          v-for="item in batches"
          :key="item.id"
          class="batch-item"
          data-testid="open-batch"
        >
          <div class="row">
            <RouterLink
              class="batch-name"
              :to="{ name: 'link', params: { token: item.token } }"
              >{{ item.name }}</RouterLink
            >
            <RouterLink
              class="icon-button"
              :to="{
                name: 'area_print',
                params: { id: area.id },
                query: { batch: item.id },
              }"
              :aria-label="`Vytisknout obchůzku ${item.name}`"
              title="Vytisknout"
            >
              <AppIcon name="print" />
            </RouterLink>
          </div>
          <BatchProgress :batch="item" />
          <div class="row">
            <BatchLink :token="item.token" />
            <RouterLink
              v-slot="{ navigate }"
              :to="{ name: 'batch', params: { id: item.id } }"
              custom
            >
              <n-button type="primary" size="small" @click="navigate">
                Potvrdit obchůzku
              </n-button>
            </RouterLink>
          </div>
        </div>
      </template>
      <div class="row">
        <n-button
          :type="batches.length ? 'default' : 'primary'"
          size="small"
          @click="dialogs.batch = true"
        >
          <template #icon><AppIcon name="plus" /></template>
          Nová obchůzka
        </n-button>
        <n-button size="small" quaternary @click="dialogs.plan = true">
          <template #icon><AppIcon name="plus" /></template>
          Nová budka
        </n-button>
      </div>
    </section>

    <section class="section">
      <div class="chips tools">
        <a class="chip dim" :href="exportUrl(area.id, 'gpx', exportParams)" download>
          <AppIcon name="down" />GPX
        </a>
        <a class="chip dim" :href="exportUrl(area.id, 'xlsx', exportParams)" download>
          <AppIcon name="down" />XLS
        </a>
        <RouterLink
          class="chip dim"
          :to="{
            name: 'area_print',
            params: { id: area.id },
            query: filterQuery(filters),
          }"
        >
          <AppIcon name="print" />Tisk
        </RouterLink>
        <button type="button" class="chip dim" @click="dialogs.gpx = true">
          <AppIcon name="up" />Import GPX
        </button>
      </div>
    </section>

    <BoxList
      :groups="[{ key: 'all', title: 'Budky', boxes: sortedShown }]"
      :selected-id="selectedId"
      :extras="extras"
      :types-by-id="typesById"
      :state-of="box => markerState(box, null)"
      @focus="focusBox"
    />

    <AreaFormDialog v-model:show="dialogs.area" :area="area" @saved="reload" />
    <NewBatchDialog
      v-model:show="dialogs.batch"
      :area-id="area.id"
      @created="onBatchCreated"
    />
    <BoxFormDialog
      v-model:show="dialogs.plan"
      :area-id="area.id"
      :center="center"
      :types="data.categories.types"
      :other-boxes="area.boxes"
      @saved="onPlanned"
    />
    <GpxImportDialog
      v-model:show="dialogs.gpx"
      :area-id="area.id"
      :types="data.categories.types"
      @imported="onImported"
    />
  </MapPanelLayout>
  <main v-else class="page"><p class="muted">Načítám…</p></main>
</template>

<style scoped>
.summary {
  padding: 18px 20px 12px;
}

.summary h2 {
  margin-top: 4px;
  font-size: 22px;
}

.title-row {
  align-items: flex-start;
  flex-wrap: nowrap;
}

.grow {
  flex: 1;
  min-width: 0;
}

.section {
  display: grid;
  gap: 12px;
  padding: 14px 20px;
  border-top: 1px solid var(--line);
}

.batch-item {
  display: grid;
  gap: 8px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--line);
}

.batch-name {
  flex: 1;
  font-size: 16px;
  font-weight: 700;
}

@media (max-width: 720px) {
  .summary {
    padding: 0 16px 10px;
  }

  .section {
    padding-left: 16px;
    padding-right: 16px;
  }
}
</style>
