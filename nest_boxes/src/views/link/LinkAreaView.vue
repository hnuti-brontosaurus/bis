<script setup>
import { computed, nextTick, ref, shallowRef } from "vue"
import { RouterLink } from "vue-router"
import { NButton } from "naive-ui"

import AppIcon from "@/components/app/AppIcon.vue"
import SegmentedControl from "@/components/app/SegmentedControl.vue"
import VolunteerHeader from "@/components/app/VolunteerHeader.vue"
import BaseMap from "@/components/map/BaseMap.vue"
import BoxMarkers from "@/components/map/BoxMarkers.vue"
import MapLegend from "@/components/map/MapLegend.vue"
import MapPanelLayout from "@/components/map/MapPanelLayout.vue"
import MarkerGlyph from "@/components/map/MarkerGlyph.vue"
import PlannedBoxes from "@/components/map/PlannedBoxes.vue"
import PositionMarker from "@/components/map/PositionMarker.vue"
import { boundsOf, distance } from "@/components/map/geometry.js"
import { checkResult, mapyLink, typeName } from "@/composables/boxes.js"
import { formatDistance, plural } from "@/composables/czech.js"
import { byId } from "@/composables/labels.js"
import { sortBoxes } from "@/composables/linkBoxes.js"
import { usePosition } from "@/composables/usePosition.js"
import { useAuthStore } from "@/data/auth.js"
import { useLinkStore } from "@/data/link.js"

const SORTS = [
  { value: "distance", label: "Nejblíž" },
  { value: "name", label: "Podle označení" },
]

const link = useLinkStore()
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
    { state: "attention", title: "Potřebuje pozornost" },
    { state: "done", title: "Hotovo" },
  ]
    .map(group => ({ ...group, rows: sortBoxes(inState([group.state])) }))
    .filter(group => group.rows.length),
)
const added = computed(() => sortBoxes(link.rows.filter(isNew)))
const total = computed(() => known.value.length)

const markers = computed(() => link.rows.filter(row => row.state !== "planned"))
const planned = computed(() => link.rows.filter(row => row.state === "planned"))
const bounds = link.payload.boxes.length
  ? boundsOf(link.payload.boxes.map(box => box.location))
  : undefined

const canManage = computed(
  () =>
    auth?.me?.is_budkar || auth?.me?.managed_area_ids.includes(link.payload.area.id),
)
const selected = computed(() => link.rows.find(row => row.id === selectedId.value))

const subtitle = row => {
  const parts = [
    row.state === "planned" ? "plánovaná" : "",
    typeName(typesById.value, row.type_id),
  ]
  if (position.value) parts.push(formatDistance(distance(position.value, row.location)))
  return parts.filter(Boolean).join(" · ")
}

const select = async id => {
  selectedId.value = id
  await nextTick()
  document.querySelector(`[data-box-row="${id}"]`)?.scrollIntoView({ block: "nearest" })
}

const focus = row => {
  selectedId.value = row.id
  map.value.flyTo({
    center: row.location.coordinates,
    zoom: Math.max(map.value.getZoom(), 17),
  })
}

const recordsLabel = count =>
  `${count} ${plural(count, "záznam", "záznamy", "záznamů")}`

const checkRoute = row => ({ name: "link_check", params: { boxId: row.id } })
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
      <RouterLink
        v-if="canManage"
        class="small manage"
        :to="{ name: 'area', params: { id: link.payload.area.id } }"
      >
        <AppIcon name="tool" />Spravovat oblast
      </RouterLink>
    </div>
    <div class="list" data-testid="box-list">
      <div
        v-for="row in toCheck"
        :key="row.id"
        class="item"
        :class="{ selected: row.id === selectedId }"
        :data-box-row="row.id"
        @click="focus(row)"
      >
        <MarkerGlyph :state="row.state" />
        <div class="text">
          <div class="name">{{ row.name || "Nová budka" }}</div>
          <div class="sub">{{ subtitle(row) }}</div>
        </div>
        <RouterLink v-slot="{ navigate }" :to="checkRoute(row)" custom>
          <n-button
            :type="row.state === 'planned' ? 'default' : 'primary'"
            size="small"
            @click.stop="navigate"
          >
            {{ row.state === "planned" ? "Pověsit" : "Zkontrolovat" }}
          </n-button>
        </RouterLink>
      </div>
      <template v-for="group in finished" :key="group.state">
        <div class="group">{{ group.title }} · {{ group.rows.length }}</div>
        <div
          v-for="row in group.rows"
          :key="row.id"
          class="item"
          :class="{ selected: row.id === selectedId }"
          :data-box-row="row.id"
          @click="focus(row)"
        >
          <MarkerGlyph :state="row.state" />
          <div class="text">
            <div class="name">{{ row.name }}</div>
            <div class="sub">
              {{ row.check ? checkResult(row.check, occupantsById) : subtitle(row) }}
            </div>
          </div>
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
        </div>
      </template>
      <template v-if="added.length">
        <div class="group">Přidané budky · {{ added.length }}</div>
        <div
          v-for="row in added"
          :key="row.id"
          class="item"
          :class="{ selected: row.id === selectedId }"
          :data-box-row="row.id"
          @click="focus(row)"
        >
          <MarkerGlyph :state="row.state" />
          <div class="text">
            <div class="name">{{ row.name }}</div>
            <div class="sub">{{ subtitle(row) }} · čeká na potvrzení správcem</div>
          </div>
          <RouterLink
            class="icon-button"
            :to="{ name: 'link_new_box', query: { budka: row.id } }"
            :aria-label="`Upravit budku ${row.name}`"
            @click.stop
          >
            <AppIcon name="edit" />
          </RouterLink>
        </div>
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
      <n-button
        v-if="selected"
        size="small"
        quaternary
        tag="a"
        :href="mapyLink(selected.location)"
        target="_blank"
      >
        <template #icon><AppIcon name="ext" /></template>
        {{ selected.name }} na Mapy.com
      </n-button>
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

.item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 20px;
  border-bottom: 1px solid var(--line);
  cursor: pointer;
}

.item.selected {
  background: var(--primary-soft);
}

.text {
  flex: 1;
  min-width: 0;
}

.name {
  font-weight: 700;
}

.sub {
  font-size: 13px;
  color: var(--muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.group {
  padding: 14px 20px 6px;
  font: 700 12px var(--font);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--muted);
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

  .item {
    padding: 10px 16px;
  }

  .group {
    padding-left: 16px;
  }
}
</style>
