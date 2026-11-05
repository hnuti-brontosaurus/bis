<script setup>
import { computed, ref } from "vue"
import { RouterLink, useRoute, useRouter } from "vue-router"
import { NButton, NImage, NImageGroup, NPopconfirm, useMessage } from "naive-ui"

import AppIcon from "@/components/app/AppIcon.vue"
import BoxFormDialog from "@/components/box/BoxFormDialog.vue"
import EndBoxDialog from "@/components/box/EndBoxDialog.vue"
import BaseMap from "@/components/map/BaseMap.vue"
import BoxMarkers from "@/components/map/BoxMarkers.vue"
import PlannedBoxes from "@/components/map/PlannedBoxes.vue"
import { aroundPoint } from "@/components/map/geometry.js"
import {
  boxChangesLabel,
  checkResult,
  describeHistory,
  holeLabel,
  mapyLink,
  typeName,
} from "@/composables/boxes.js"
import { formatDate, formatDistance, seasonLabel } from "@/composables/czech.js"
import {
  BOX_LEFT_LABELS,
  byId,
  HANGING_STATUSES,
  MATERIAL_LABELS,
  OPENING_LABELS,
  STATUS_LABELS,
} from "@/composables/labels.js"
import { useLoad } from "@/composables/useLoad.js"
import { reportError } from "@/data/errors.js"
import {
  deleteBox,
  getArea,
  getBox,
  getBoxHistory,
  getCategories,
  listChecks,
} from "@/data/manage.js"

const route = useRoute()
const router = useRouter()
const message = useMessage()

const { data, reload } = useLoad(async () => {
  const [box, categories, checks, history] = await Promise.all([
    getBox(route.params.id),
    getCategories(),
    listChecks({ box: route.params.id }),
    getBoxHistory(route.params.id),
  ])
  const area = await getArea(box.area_id)
  return { box, area, categories, checks, history }
})

const dialogs = ref({ edit: false, end: false })

const box = computed(() => data.value?.box)
const typesById = computed(() => byId(data.value?.categories.types ?? []))
const occupantsById = computed(() => byId(data.value?.categories.occupants ?? []))
const endReasonsById = computed(() => byId(data.value?.categories.end_reasons ?? []))
const usable = computed(() => box.value.status !== "ended")

const STATUS_TONES = {
  in_use: "ok",
  needs_repair: "warn",
  needs_replacing: "bad",
  planned: "info",
  missing: "bad",
  taken_down: "warn",
}

const neighbours = computed(() =>
  data.value.area.boxes
    .filter(
      other => other.id !== box.value.id && HANGING_STATUSES.includes(other.status),
    )
    .map(other => ({ ...other, state: "out" })),
)
const marker = computed(() =>
  box.value.status === "planned"
    ? []
    : [{ ...box.value, state: box.value.season_state ?? "out" }],
)

const facts = computed(() => [
  ["Typ", typeName(typesById.value, box.value.type_id)],
  ["Otvor", holeLabel(box.value) || "–"],
  ["Otevírání", OPENING_LABELS[box.value.opening] ?? "–"],
  ["Materiál", MATERIAL_LABELS[box.value.material] ?? "–"],
  ["Vyvěšena", formatDate(box.value.installed_on)],
  ["Nejbližší budka", formatDistance(box.value.closest_distance)],
  ["Nejbližší stejného typu", formatDistance(box.value.closest_same_type_distance)],
  [
    "Nadmořská výška",
    box.value.elevation === null ? "–" : `${box.value.elevation} m n. m.`,
  ],
  [
    "Poloha",
    `${box.value.location.coordinates[1].toFixed(5)}, ${box.value.location.coordinates[0].toFixed(5)}`,
  ],
  ["Dřívější označení", box.value.previous_names || "–"],
  ...(box.value.status === "ended"
    ? [
        ["Ukončena", formatDate(box.value.ended_on)],
        ["Důvod", endReasonsById.value.get(box.value.end_reason_id)?.name ?? "–"],
      ]
    : []),
])

const who = check =>
  check.volunteer_nickname ||
  (check.entered_by
    ? `${check.entered_by.first_name} ${check.entered_by.last_name}`
    : "") ||
  (check.is_historical ? "starý BIS" : "–")

const historyContext = computed(() => ({
  typesById: typesById.value,
  endReasonsById: endReasonsById.value,
}))

const remove = async () => {
  try {
    await deleteBox(box.value.id)
    message.success("Plánovaná budka je smazaná.")
    await router.push({ name: "area", params: { id: data.value.area.id } })
  } catch (error) {
    reportError(error)
  }
}

const onEnded = async () => {
  message.success("Budka je ukončená.")
  await reload()
}

const onSaved = async saved => {
  message.success("Budka je uložená.")
  await reload()
  if (saved.warnings.spacing.length)
    message.warning(
      `Pozor, budka je blízko ${saved.warnings.spacing.map(item => item.box_name).join(", ")}.`,
    )
}
</script>

<template>
  <main v-if="data" class="page box-page">
    <div class="crumb">
      <RouterLink :to="{ name: 'areas' }">Mapa</RouterLink>
      <AppIcon name="chev" />
      <RouterLink :to="{ name: 'area', params: { id: data.area.id } }">
        {{ data.area.name }}
      </RouterLink>
      <AppIcon name="chev" />
      <span>{{ box.name }}</span>
    </div>
    <div class="row title-row">
      <h1 class="num">{{ box.name }}</h1>
      <span class="tag" :class="STATUS_TONES[box.status]">{{
        STATUS_LABELS[box.status]
      }}</span>
      <span v-if="box.is_verified" class="tag info">ověřená</span>
      <span v-else class="tag warn">neověřená</span>
      <span class="spacer" />
      <RouterLink
        v-if="usable"
        v-slot="{ navigate }"
        :to="{ name: 'check', params: { id: box.id } }"
        custom
      >
        <n-button type="primary" @click="navigate">
          <template #icon><AppIcon name="plus" /></template>
          {{ box.status === "planned" ? "Zapsat pověšení" : "Zadat kontrolu" }}
        </n-button>
      </RouterLink>
      <n-button v-if="usable" @click="dialogs.edit = true">
        <template #icon><AppIcon name="edit" /></template>
        Upravit
      </n-button>
      <n-button tag="a" :href="mapyLink(box.location)" target="_blank" quaternary>
        <template #icon><AppIcon name="ext" /></template>
        Mapy.com
      </n-button>
    </div>

    <div v-if="box.should_be_moved" class="note warn">
      <AppIcon name="warn" />
      <div>
        <b>Visí moc blízko jiné budky</b>
        Nejbližší je {{ formatDistance(box.closest_distance) }} odsud, stejného typu
        {{ formatDistance(box.closest_same_type_distance) }}. Zvaž, jestli ji
        nepřevěsit.
      </div>
    </div>

    <div class="two">
      <div class="card stack">
        <dl class="facts">
          <div v-for="[term, value] in facts" :key="term">
            <dt>{{ term }}</dt>
            <dd class="num">{{ value }}</dd>
          </div>
        </dl>
        <div v-if="box.note" class="small">
          <b>Poznámka pro dobrovolníky:</b> {{ box.note }}
        </div>
      </div>
      <div class="minimap">
        <BaseMap :bounds="aroundPoint(box.location.coordinates)">
          <PlannedBoxes v-if="box.status === 'planned'" :boxes="[box]" />
          <BoxMarkers :boxes="[...neighbours, ...marker]" :selected-id="box.id" />
        </BaseMap>
      </div>
    </div>

    <h2 class="section-heading">Historie kontrol</h2>
    <div v-if="data.checks.length" class="scroll-x">
      <table class="tbl" data-testid="check-history">
        <thead>
          <tr>
            <th>Sezóna</th>
            <th>Datum</th>
            <th>Výsledek</th>
            <th>Stav budky</th>
            <th>Kdo</th>
            <th>Fotky</th>
            <th />
          </tr>
        </thead>
        <tbody>
          <tr v-for="check in data.checks" :key="check.id">
            <td class="num">
              <b>{{ seasonLabel(check.season) }}</b>
            </td>
            <td class="num">{{ formatDate(check.date) }}</td>
            <td>
              <b>{{ checkResult(check, occupantsById) }}</b>
              <div v-if="Object.keys(check.box_changes).length">
                <span class="tag info">
                  <AppIcon name="edit" />{{
                    boxChangesLabel(check.box_changes, typesById)
                  }}
                </span>
              </div>
              <div v-if="check.note" class="small muted">{{ check.note }}</div>
            </td>
            <td>{{ BOX_LEFT_LABELS[check.box_left] ?? "–" }}</td>
            <td>{{ who(check) }}</td>
            <td>
              <n-image-group v-if="check.photos.length">
                <div class="thumbs">
                  <n-image
                    v-for="photo in check.photos"
                    :key="photo.id"
                    :src="photo.photo.small"
                    :preview-src="photo.photo.large"
                    width="44"
                    height="44"
                    object-fit="cover"
                  />
                </div>
              </n-image-group>
            </td>
            <td class="actions">
              <span class="tag" :class="check.is_confirmed ? 'ok' : 'warn'">
                {{ check.is_confirmed ? "potvrzeno" : "čeká" }}
              </span>
              <RouterLink
                :to="{
                  name: 'check',
                  params: { id: box.id },
                  query: { check: check.id },
                }"
                :aria-label="`Upravit kontrolu z ${formatDate(check.date)}`"
              >
                <AppIcon name="edit" />
              </RouterLink>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <p v-else class="muted">Budka zatím nemá žádnou kontrolu.</p>

    <template v-if="data.history.length">
      <h2 class="section-heading">Změny budky</h2>
      <ul class="history">
        <li v-for="entry in data.history" :key="entry.id">
          <span class="num muted">{{ formatDate(entry.date) }}</span>
          <span>
            {{ describeHistory(entry.changes, historyContext) }}
          </span>
          <span class="muted small">
            {{ entry.user ? `${entry.user.first_name} ${entry.user.last_name}` : "" }}
            {{ entry.box_check_id ? "· kontrolou" : "" }}
          </span>
        </li>
      </ul>
    </template>

    <div v-if="box.status === 'planned'" class="row">
      <n-popconfirm @positive-click="remove">
        <template #trigger>
          <n-button type="error" ghost size="small">
            <template #icon><AppIcon name="x" /></template>
            Smazat
          </n-button>
        </template>
        Budku nikdo nepověsí? Smaže se i s historií.
      </n-popconfirm>
    </div>
    <div v-else-if="usable" class="row">
      <n-button type="error" ghost size="small" @click="dialogs.end = true">
        <template #icon><AppIcon name="x" /></template>
        Ukončit budku
      </n-button>
      <span class="small muted">
        Zničená, nahrazená nebo potvrzeně ztracená. Ukončenou budku nejde obnovit.
      </span>
    </div>

    <BoxFormDialog
      v-model:show="dialogs.edit"
      :box="box"
      :area-id="box.area_id"
      :center="box.location"
      :types="data.categories.types"
      @saved="onSaved"
    />
    <EndBoxDialog
      v-model:show="dialogs.end"
      :box="box"
      :end-reasons="data.categories.end_reasons"
      @ended="onEnded"
    />
  </main>
  <main v-else class="page"><p class="muted">Načítám…</p></main>
</template>

<style scoped>
.box-page {
  gap: 20px;
}

.title-row {
  align-items: center;
}

.minimap {
  height: 100%;
  min-height: 300px;
  border-radius: var(--r);
  overflow: hidden;
  border: 1px solid var(--line);
}

.thumbs {
  display: flex;
  gap: 4px;
}

.thumbs :deep(img) {
  border-radius: 6px;
}

.actions {
  white-space: nowrap;
}

.actions a {
  margin-left: 8px;
  vertical-align: middle;
}

.history {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 8px;
}

.history li {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--line);
}
</style>
