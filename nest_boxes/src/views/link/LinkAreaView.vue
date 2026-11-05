<script setup>
import { computed, nextTick, ref, shallowRef, watch } from "vue"
import { RouterLink, useRouter } from "vue-router"
import { NButton } from "naive-ui"

import AppIcon from "@/components/app/AppIcon.vue"
import SegmentedControl from "@/components/app/SegmentedControl.vue"
import VolunteerHeader from "@/components/app/VolunteerHeader.vue"
import BaseMap from "@/components/map/BaseMap.vue"
import BoxMarkers from "@/components/map/BoxMarkers.vue"
import BatchLink from "@/components/batch/BatchLink.vue"
import BoxItem from "@/components/box/BoxItem.vue"
import MapLegend from "@/components/map/MapLegend.vue"
import MapPanelLayout from "@/components/map/MapPanelLayout.vue"
import PlannedBoxes from "@/components/map/PlannedBoxes.vue"
import PositionMarker from "@/components/map/PositionMarker.vue"
import { boundsOf, distance } from "@/components/map/geometry.js"
import { ACTIVE_STATUSES } from "@/composables/areaBoxes.js"
import { checkResult } from "@/composables/boxes.js"
import { formatDistance, plural } from "@/composables/czech.js"
import { byId } from "@/composables/labels.js"
import { sortBoxes } from "@/composables/linkBoxes.js"
import { usePosition } from "@/composables/usePosition.js"
import { useAuthStore } from "@/data/auth.js"
import { reportError } from "@/data/errors.js"
import { addBatchBoxes, getArea, removeBatchBoxes } from "@/data/manage.js"
import { useLinkStore } from "@/data/link.js"

const SORTS = [
  { value: "distance", label: "Nejblíž" },
  { value: "name", label: "Podle označení" },
]

const link = useLinkStore()
const router = useRouter()
// whoami needs signal, and offline its failure would only be noise
const auth = navigator.onLine ? useAuthStore() : null
const position = usePosition()

const map = shallowRef(null)
const selectedId = ref(null)
const sort = ref("distance")

const typesById = computed(() => byId(link.payload.categories.types))
const occupantsById = computed(() => byId(link.payload.categories.occupants))

const isNew = row => row.is_new
const known = computed(() => link.rows.filter(row => !isNew(row)))
const inState = states => known.value.filter(row => states.includes(row.state))
const toCheck = computed(() =>
  sortBoxes(
    inState(["to_check", "planned"]),
    sort.value === "distance" ? position.value : null,
  ),
)
const finished = computed(() =>
  [
    { state: "attention", title: "K opravě" },
    { state: "done", title: "Hotovo" },
  ]
    .map(group => ({ ...group, rows: sortBoxes(inState([group.state])) }))
    .filter(group => group.rows.length),
)
const added = computed(() => sortBoxes(link.rows.filter(isNew)))
const total = computed(() => known.value.length)

// A manager of the area edits the batch here: the area's other boxes, to add
const areaBoxes = shallowRef([])
const showsOutside = ref(false)
const outside = computed(() => {
  const inBatch = new Set(link.rows.map(row => row.id))
  return sortBoxes(
    areaBoxes.value.filter(
      box => ACTIVE_STATUSES.includes(box.status) && !inBatch.has(box.id),
    ),
  )
})

const markers = computed(() => [
  ...link.rows.filter(row => row.state !== "planned"),
  ...(showsOutside.value
    ? outside.value
        .filter(box => box.status !== "planned")
        .map(box => ({ ...box, state: "out" }))
    : []),
])
const planned = computed(() => link.rows.filter(row => row.state === "planned"))
const bounds = link.payload.boxes.length
  ? boundsOf(link.payload.boxes.map(box => box.location))
  : undefined

const canManage = computed(() => Boolean(auth?.isManager))

const away = row =>
  position.value ? formatDistance(distance(position.value, row.location)) : ""

// A second click on a batch box's marker opens its check, as on the manager maps
const select = async id => {
  if (id === selectedId.value && link.rows.some(row => row.id === id))
    return router.push(checkRoute({ id }))
  selectedId.value = id
  await nextTick()
  document.querySelector(`[data-box-row="${id}"]`)?.scrollIntoView({ block: "nearest" })
}

// The selected row shows the box's detail; a click on it again closes that
const focus = row => {
  if (row.id === selectedId.value) {
    selectedId.value = null
    return
  }
  selectedId.value = row.id
  map.value.flyTo({
    center: row.location.coordinates,
    zoom: Math.max(map.value.getZoom(), 17),
  })
}

const recordsLabel = count =>
  `${count} ${plural(count, "záznam", "záznamy", "záznamů")}`

const checkRoute = row => ({ name: "link_check", params: { boxId: row.id } })

const loadArea = async () => {
  areaBoxes.value = (await getArea(link.payload.area.id)).boxes
}

watch(canManage, manages => manages && loadArea().catch(reportError), {
  immediate: true,
})

const changing = ref(null)
const changeBatch = async (box, add) => {
  changing.value = box.id
  try {
    await (add ? addBatchBoxes : removeBatchBoxes)(link.payload.batch.id, [box.id])
    await link.refresh()
  } catch (error) {
    reportError(error)
  } finally {
    changing.value = null
  }
}
</script>

<template>
  <VolunteerHeader
    :title="link.payload.area.name"
    :subtitle="link.payload.batch.name"
    :pending="link.pending"
  />
  <MapPanelLayout>
    <template #map="{ bottomInset }">
      <BaseMap :bounds="bounds" :bottom-inset="bottomInset" @ready="map = $event">
        <PlannedBoxes :boxes="planned" />
        <BoxMarkers :boxes="markers" :selected-id="selectedId" @select="select" />
        <PositionMarker :position="position" />
      </BaseMap>
    </template>
    <template #summary>
      <div class="summary">
        <div class="row count-row">
          <div class="big-count num" data-testid="remaining">
            zbývá {{ toCheck.length }} <small>z {{ total }}</small>
          </div>
          <span class="spacer" />
          <span v-if="link.prefetch.state === 'ready'" class="tag ok">
            <AppIcon name="check" />offline připraveno
          </span>
          <span v-else-if="link.prefetch.state === 'partial'" class="tag warn">
            <AppIcon name="warn" />mapa jen zčásti
          </span>
          <span v-else class="tag num">
            <AppIcon name="cloud" />mapa {{ link.prefetch.done }} /
            {{ link.prefetch.total }}
          </span>
        </div>
        <div class="prog">
          <i
            :style="{
              width: `${total ? ((total - toCheck.length) / total) * 100 : 0}%`,
            }"
          />
        </div>
      </div>
    </template>
    <div class="controls">
      <SegmentedControl v-model="sort" :options="SORTS" size="sm" />
      <p v-if="sort === 'distance' && !position" class="small muted">
        Čekám na polohu telefonu, zatím řadím podle označení.
      </p>
      <MapLegend class="hide-sm" />
      <div v-if="link.rejected.length" class="note bad">
        <AppIcon name="warn" />
        <div>
          <b>Server odmítl {{ recordsLabel(link.rejected.length) }}</b>
          Zůstává to v telefonu. Dej prosím vědět správci oblasti.
        </div>
      </div>
      <div v-if="canManage" class="row manage-row">
        <BatchLink :token="link.payload.batch.token" />
        <RouterLink
          class="small manage"
          :to="{ name: 'area', params: { id: link.payload.area.id } }"
        >
          <AppIcon name="tool" />Spravovat oblast
        </RouterLink>
      </div>
    </div>
    <div class="list" data-testid="box-list">
      <BoxItem
        v-for="row in toCheck"
        :key="row.id"
        :box="row"
        :state="row.state"
        :expanded="row.id === selectedId"
        :types-by-id="typesById"
        :aside="away(row)"
        @toggle="focus(row)"
      >
        <template #action>
          <RouterLink v-slot="{ navigate }" :to="checkRoute(row)" custom>
            <n-button
              :type="row.state === 'planned' ? 'default' : 'primary'"
              size="small"
              @click.stop="navigate"
            >
              {{ row.state === "planned" ? "Pověsit" : "Zkontrolovat" }}
            </n-button>
          </RouterLink>
        </template>
        <template #extra>
          <n-button
            v-if="canManage"
            size="small"
            :loading="changing === row.id"
            @click.stop="changeBatch(row, false)"
          >
            <template #icon><AppIcon name="minus" /></template>
            Vyřadit z obchůzky
          </n-button>
        </template>
      </BoxItem>
      <template v-for="group in finished" :key="group.state">
        <div class="group">{{ group.title }} · {{ group.rows.length }}</div>
        <BoxItem
          v-for="row in group.rows"
          :key="row.id"
          :box="row"
          :state="row.state"
          :expanded="row.id === selectedId"
          :types-by-id="typesById"
          :aside="away(row)"
          @toggle="focus(row)"
        >
          <template #action>
            <RouterLink
              v-if="row.check"
              class="icon-button"
              :to="checkRoute(row)"
              :aria-label="`Upravit kontrolu budky ${row.name}`"
              @click.stop
            >
              <AppIcon name="edit" />
            </RouterLink>
            <RouterLink v-else v-slot="{ navigate }" :to="checkRoute(row)" custom>
              <n-button size="small" secondary @click.stop="navigate">
                Zkontrolovat
              </n-button>
            </RouterLink>
          </template>
          <template #extra>
            <p v-if="row.check" class="small muted">
              Letos: {{ checkResult(row.check, occupantsById) }}
            </p>
            <n-button
              v-if="canManage"
              size="small"
              :loading="changing === row.id"
              @click.stop="changeBatch(row, false)"
            >
              <template #icon><AppIcon name="minus" /></template>
              Vyřadit z obchůzky
            </n-button>
          </template>
        </BoxItem>
      </template>
      <template v-if="added.length">
        <div class="group">Přidané budky · {{ added.length }}</div>
        <BoxItem
          v-for="row in added"
          :key="row.id"
          :box="row"
          :state="row.state"
          :expanded="row.id === selectedId"
          :types-by-id="typesById"
          :aside="away(row)"
          @toggle="focus(row)"
        >
          <template #tags>
            <span class="tag warn">čeká na potvrzení správcem</span>
          </template>
          <template #action>
            <RouterLink
              class="icon-button"
              :to="{ name: 'link_new_box', query: { budka: row.id } }"
              :aria-label="`Upravit budku ${row.name}`"
              @click.stop
            >
              <AppIcon name="edit" />
            </RouterLink>
          </template>
          <template #extra> </template>
        </BoxItem>
      </template>
      <template v-if="canManage && outside.length">
        <button
          type="button"
          class="group toggle"
          :aria-expanded="showsOutside"
          @click="showsOutside = !showsOutside"
        >
          Mimo obchůzku · {{ outside.length }}
          <AppIcon :name="showsOutside ? 'minus' : 'chevd'" />
        </button>
        <template v-if="showsOutside">
          <BoxItem
            v-for="row in outside"
            :key="row.id"
            :box="row"
            state="out"
            :expanded="row.id === selectedId"
            :types-by-id="typesById"
            :aside="away(row)"
            @toggle="focus(row)"
          >
            <template #action>
              <n-button
                size="small"
                :loading="changing === row.id"
                :aria-label="`Přidat do obchůzky ${row.name}`"
                @click.stop="changeBatch(row, true)"
              >
                <template #icon><AppIcon name="plus" /></template>
                Přidat
              </n-button>
            </template>
            <template #extra> </template>
          </BoxItem>
        </template>
      </template>
    </div>
    <div class="foot">
      <RouterLink v-slot="{ navigate }" :to="{ name: 'link_new_box' }" custom>
        <n-button size="small" @click="navigate">
          <template #icon><AppIcon name="plus" /></template>
          Nová budka
        </n-button>
      </RouterLink>
      <RouterLink v-slot="{ navigate }" :to="{ name: 'link_help' }" custom>
        <n-button size="small" quaternary @click="navigate">
          <template #icon><AppIcon name="help" /></template>
          Nápověda
        </n-button>
      </RouterLink>
    </div>
  </MapPanelLayout>
</template>

<style scoped>
.summary {
  padding: 12px 20px 14px;
  display: grid;
  gap: 10px;
}

.count-row {
  align-items: flex-end;
  flex-wrap: nowrap;
}

.big-count {
  font-size: 30px;
  font-weight: 800;
  line-height: 1;
  letter-spacing: -0.01em;
  white-space: nowrap;
}

.big-count small {
  font-size: 17px;
  color: var(--muted);
  font-weight: 700;
}

.controls {
  padding: 0 20px 12px;
  display: grid;
  gap: 10px;
  border-bottom: 1px solid var(--line);
}

.manage-row {
  align-items: center;
  gap: 12px;
}

.manage {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-weight: 700;
}

.manage .icon {
  width: 16px;
  height: 16px;
}

.group {
  padding: 14px 20px 6px;
  font: 700 12px var(--font);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--muted);
}

.group.toggle {
  display: flex;
  align-items: center;
  gap: 6px;
  width: 100%;
  border: 0;
  border-top: 1px solid var(--line);
  background: none;
  cursor: pointer;
  text-align: left;
}

.group.toggle .icon {
  width: 14px;
  height: 14px;
}

.foot {
  position: sticky;
  bottom: 0;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 12px 20px;
  border-top: 1px solid var(--line);
  background: var(--surface);
}

@media (max-width: 720px) {
  .summary {
    padding: 0 16px 12px;
  }

  .controls,
  .foot {
    padding-left: 16px;
    padding-right: 16px;
  }

  .group {
    padding-left: 16px;
  }
}
</style>
