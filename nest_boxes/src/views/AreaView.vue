<script setup>
import { computed, nextTick, ref, shallowRef, watch } from "vue"
import { RouterLink, useRoute, useRouter } from "vue-router"
import { NButton, NPopconfirm, NSelect, useMessage } from "naive-ui"

import AppIcon from "@/components/app/AppIcon.vue"
import AreaFormDialog from "@/components/area/AreaFormDialog.vue"
import GpxImportDialog from "@/components/area/GpxImportDialog.vue"
import NewBatchDialog from "@/components/area/NewBatchDialog.vue"
import BatchLink from "@/components/batch/BatchLink.vue"
import BatchProgress from "@/components/batch/BatchProgress.vue"
import BoxFilters from "@/components/box/BoxFilters.vue"
import BoxFormDialog from "@/components/box/BoxFormDialog.vue"
import BoxList from "@/components/box/BoxList.vue"
import BaseMap from "@/components/map/BaseMap.vue"
import BoxMarkers from "@/components/map/BoxMarkers.vue"
import MapLegend from "@/components/map/MapLegend.vue"
import MapPanelLayout from "@/components/map/MapPanelLayout.vue"
import PlannedBoxes from "@/components/map/PlannedBoxes.vue"
import { boundsOf } from "@/components/map/geometry.js"
import {
  ACTIVE_STATUSES,
  boxRowDetail,
  defaultFilters,
  filterBoxes,
  filterParams,
  markerState,
  splitByBatch,
} from "@/composables/areaBoxes.js"
import { boxCountLabel, currentSeason } from "@/composables/czech.js"
import { byId } from "@/composables/labels.js"
import { latestChecks } from "@/composables/linkBoxes.js"
import { useLoad } from "@/composables/useLoad.js"
import { CZECHIA_BOUNDS } from "@/config.js"
import { useAuthStore } from "@/data/auth.js"
import { reportError } from "@/data/errors.js"
import {
  addBatchBoxes,
  closeBatch,
  exportUrl,
  getArea,
  getCategories,
  listBatches,
  listChecks,
  removeBatchBoxes,
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
const filters = ref(defaultFilters())
const dialogs = ref({ area: false, batch: false, plan: false, gpx: false })

const area = computed(() => data.value?.area)
const batches = computed(() => data.value?.batches ?? [])
const typesById = computed(() => byId(data.value?.categories.types ?? []))
const occupantsById = computed(() => byId(data.value?.categories.occupants ?? []))

const batchId = computed(() =>
  route.query.batch ? Number(route.query.batch) : (batches.value[0]?.id ?? null),
)
const batch = computed(() => batches.value.find(item => item.id === batchId.value))
const otherBatches = computed(() => batches.value.filter(item => item !== batch.value))
const batchOptions = computed(() =>
  batches.value.map(item => ({ value: item.id, label: item.name })),
)
const selectBatch = id => router.replace({ query: { ...route.query, batch: id } })

const shown = computed(() =>
  area.value ? filterBoxes(area.value.boxes, filters.value, season) : [],
)
const groups = computed(() => splitByBatch(shown.value, batch.value))
const checkOf = box => data.value.checks.get(box.id)

const detail = box =>
  boxRowDetail(box, checkOf(box), {
    typesById: typesById.value,
    occupantsById: occupantsById.value,
    otherBatches: otherBatches.value,
  })

const markerBoxes = computed(() =>
  shown.value
    .filter(box => box.status !== "planned")
    .map(box => ({ ...box, state: markerState(box, batch.value) })),
)
const plannedBoxes = computed(() =>
  shown.value.filter(
    box =>
      box.status === "planned" &&
      (!batch.value || batch.value.box_ids.includes(box.id)),
  ),
)

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

const summary = computed(() =>
  batch.value
    ? `${batch.value.checked_count} z ${batch.value.box_count} zkontrolováno`
    : boxCountLabel(shown.value.length),
)

const unverifiedCount = computed(
  () =>
    area.value.boxes.filter(
      box => !box.is_verified && ACTIVE_STATUSES.includes(box.status),
    ).length,
)
const exportParams = computed(() => ({
  ...filterParams(filters.value, season),
  ...(batch.value && { batch: batch.value.id }),
}))

const selectBox = async id => {
  selectedId.value = id
  await nextTick()
  document.querySelector(`[data-box-row="${id}"]`)?.scrollIntoView({ block: "nearest" })
}

const focusBox = box => {
  selectedId.value = box.id
  map.value?.easeTo({
    center: box.location.coordinates,
    zoom: Math.max(map.value.getZoom(), 16),
  })
}

const replaceBatch = updated => {
  data.value = {
    ...data.value,
    batches: data.value.batches.map(item => (item.id === updated.id ? updated : item)),
  }
}

const move = async (box, into) => {
  try {
    replaceBatch(
      await (into ? addBatchBoxes : removeBatchBoxes)(batch.value.id, [box.id]),
    )
  } catch (error) {
    reportError(error)
  }
}

const close = async () => {
  try {
    await closeBatch(batch.value.id)
    message.success("Obchůzka je uzavřená, odkaz už nic nepřijímá.")
    await router.replace({ query: {} })
    await reload()
    auth.refresh()
  } catch (error) {
    reportError(error)
  }
}

const onBatchCreated = async created => {
  await reload()
  await selectBatch(created.id)
  auth.refresh()
}

const onPlanned = async box => {
  message.success(`Budka ${box.name} je naplánovaná.`)
  await reload()
}

const onImported = async count => {
  message.success(`Import je hotový, změněných budek: ${count}.`)
  await reload()
}

watch(batchId, () => (selectedId.value = null))
</script>

<template>
  <MapPanelLayout v-if="data">
    <template #map="{ bottomInset }">
      <BaseMap :bounds="bounds" :bottom-inset="bottomInset" @ready="map = $event">
        <PlannedBoxes :boxes="plannedBoxes" />
        <BoxMarkers
          :boxes="markerBoxes"
          :selected-id="selectedId"
          @select="selectBox"
        />
      </BaseMap>
    </template>
    <template #summary>
      <div class="summary">
        <div class="row title-row">
          <div class="grow">
            <p class="eyebrow">{{ area.administration_unit.name }}</p>
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
      <template v-if="batch">
        <div class="row">
          <n-select
            v-if="batches.length > 1"
            :value="batch.id"
            :options="batchOptions"
            size="small"
            class="grow"
            @update:value="selectBatch"
          />
          <b v-else class="batch-name">{{ batch.name }}</b>
          <n-button size="small" quaternary @click="dialogs.batch = true">
            <template #icon><AppIcon name="plus" /></template>
            Nová obchůzka
          </n-button>
        </div>
        <BatchProgress :batch="batch" />
        <BatchLink :token="batch.token" />
        <div class="row">
          <RouterLink
            v-slot="{ navigate }"
            :to="{ name: 'batch', params: { id: batch.id } }"
            custom
          >
            <n-button type="primary" size="small" @click="navigate">
              Zkontrolovat a potvrdit
            </n-button>
          </RouterLink>
          <n-popconfirm @positive-click="close">
            <template #trigger>
              <n-button size="small">Uzavřít</n-button>
            </template>
            Uzavřít obchůzku bez potvrzení? Odkaz přestane přijímat kontroly, ty
            čekající zůstanou nepotvrzené.
          </n-popconfirm>
          <n-button
            class="push-end"
            size="small"
            quaternary
            @click="dialogs.plan = true"
          >
            <template #icon><AppIcon name="plus" /></template>
            Naplánovat budku
          </n-button>
        </div>
      </template>
      <template v-else>
        <p class="muted">Žádná otevřená obchůzka.</p>
        <div class="row">
          <n-button type="primary" size="small" @click="dialogs.batch = true">
            <template #icon><AppIcon name="plus" /></template>
            Vytvořit obchůzku
          </n-button>
          <n-button size="small" quaternary @click="dialogs.plan = true">
            <template #icon><AppIcon name="plus" /></template>
            Naplánovat budku
          </n-button>
        </div>
      </template>
    </section>

    <section class="section filters">
      <BoxFilters
        v-model="filters"
        :types="data.categories.types"
        :unverified-count="unverifiedCount"
      />
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
            query: { batch: batch?.id, filters: JSON.stringify(filters) },
          }"
        >
          <AppIcon name="print" />Tisk
        </RouterLink>
        <button type="button" class="chip dim" @click="dialogs.gpx = true">
          <AppIcon name="up" />Import GPX
        </button>
      </div>
      <MapLegend class="hide-sm" />
    </section>

    <BoxList
      :groups="
        batch
          ? [
              { key: 'in', title: 'V této obchůzce', boxes: groups.inBatch },
              { key: 'out', title: 'Mimo obchůzku', boxes: groups.outside },
            ]
          : [{ key: 'all', title: 'Budky', boxes: groups.outside }]
      "
      :selected-id="selectedId"
      :detail="detail"
      :state-of="box => markerState(box, batch)"
      @focus="focusBox"
    >
      <template v-if="batch" #action="{ box, group }">
        <button
          type="button"
          class="move"
          :title="group.key === 'in' ? 'Vyřadit z obchůzky' : 'Přidat do obchůzky'"
          :aria-label="`${group.key === 'in' ? 'Vyřadit z obchůzky' : 'Přidat do obchůzky'} ${box.name}`"
          @click.stop="move(box, group.key !== 'in')"
        >
          <AppIcon :name="group.key === 'in' ? 'minus' : 'plus'" />
        </button>
      </template>
    </BoxList>

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
      :batch-id="batch?.id ?? null"
      :types="data.categories.types"
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

.push-end {
  margin-left: auto;
}

.batch-name {
  flex: 1;
  font-size: 16px;
}

.move {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: 1px solid var(--line-strong);
  background: var(--surface);
  color: var(--muted);
  display: grid;
  place-items: center;
  cursor: pointer;
  flex: none;
}

.move .icon {
  width: 16px;
  height: 16px;
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
