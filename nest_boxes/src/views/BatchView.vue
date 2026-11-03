<script setup>
import { computed, ref } from "vue"
import { RouterLink, useRoute } from "vue-router"
import { NButton, NPopconfirm, NSelect, useMessage } from "naive-ui"

import AppIcon from "@/components/app/AppIcon.vue"
import BatchLink from "@/components/batch/BatchLink.vue"
import BatchProgress from "@/components/batch/BatchProgress.vue"
import CheckForm from "@/components/check/CheckForm.vue"
import MarkerGlyph from "@/components/map/MarkerGlyph.vue"
import { batchHighlights, batchTiles } from "@/composables/batchSummary.js"
import { boxChangesLabel, checkResult, reportedState } from "@/composables/boxes.js"
import {
  checkCountLabel,
  formatDate,
  isoDate,
  pendingLabel,
} from "@/composables/czech.js"
import { BOX_LEFT_LABELS, byId, CLEANING_LABELS } from "@/composables/labels.js"
import { compareNames } from "@/composables/linkBoxes.js"
import { useLoad } from "@/composables/useLoad.js"
import { useAuthStore } from "@/data/auth.js"
import { reportError } from "@/data/errors.js"
import {
  confirmBatch,
  createCheck,
  deleteCheck,
  getArea,
  getBatch,
  getCategories,
  listChecks,
  listHelpArticles,
  saveCheckPhotos,
  updateCheck,
} from "@/data/manage.js"

const ENTERABLE = ["in_use", "planned", "missing", "taken_down"]

const route = useRoute()
const message = useMessage()
const auth = useAuthStore()

const { data, reload } = useLoad(async () => {
  const [batch, checks, categories, helpArticles] = await Promise.all([
    getBatch(route.params.id),
    listChecks({ batch: route.params.id }),
    getCategories(),
    listHelpArticles(),
  ])
  const area = await getArea(batch.area_id)
  return { batch, checks, categories, helpArticles, area }
})

const editingId = ref(null)
const adding = ref({ boxId: null, date: isoDate(), key: 0 })

const batch = computed(() => data.value?.batch)
const boxesById = computed(() => byId(data.value?.area.boxes ?? []))
const typesById = computed(() => byId(data.value?.categories.types ?? []))
const occupantsById = computed(() => byId(data.value?.categories.occupants ?? []))
const checks = computed(() =>
  [...data.value.checks].sort((a, b) =>
    compareNames(boxesById.value.get(a.box_id), boxesById.value.get(b.box_id)),
  ),
)
const newBoxes = computed(() =>
  data.value.area.boxes.filter(
    box => box.batch_id === batch.value.id && !box.is_confirmed,
  ),
)
const tiles = computed(() => batchTiles(batch.value, data.value.checks, newBoxes.value))
const highlights = computed(() =>
  batchHighlights(checks.value, newBoxes.value, {
    boxesById: boxesById.value,
    typesById: typesById.value,
  }),
)

// The batch's unchecked boxes first, then the rest of the area
const addOptions = computed(() => {
  const checked = new Set(data.value.checks.map(check => check.box_id))
  const inBatch = new Set(batch.value.box_ids)
  return data.value.area.boxes
    .filter(box => ENTERABLE.includes(box.status) && !checked.has(box.id))
    .sort((a, b) => inBatch.has(b.id) - inBatch.has(a.id) || compareNames(a, b))
    .map(box => ({
      value: box.id,
      label: inBatch.has(box.id) ? box.name : `${box.name} (mimo dávku)`,
    }))
})
const addingBox = computed(() => boxesById.value.get(adding.value.boxId))

const yesNo = value => (value ? "ano" : "ne")
const who = check =>
  check.volunteer_nickname ||
  (check.entered_by ? check.entered_by.first_name : "") ||
  "–"

const saveEdit = async (values, photos) => {
  const saved = await updateCheck(editingId.value, values)
  await saveCheckPhotos(saved, photos)
  editingId.value = null
  message.success("Kontrola je upravená.")
  await reload()
}

const saveNew = async (values, photos) => {
  const saved = await createCheck({ ...values, batch_id: batch.value.id })
  await saveCheckPhotos(saved, photos)
  message.success(`Kontrola budky ${addingBox.value.name} je zapsaná.`)
  adding.value = { boxId: null, date: values.date, key: adding.value.key + 1 }
  await reload()
}

const remove = async check => {
  try {
    await deleteCheck(check.id)
    editingId.value = null
    message.success("Kontrola je smazaná.")
    await reload()
  } catch (error) {
    reportError(error)
  }
}

const confirm = async () => {
  try {
    await confirmBatch(batch.value.id)
    message.success("Dávka je potvrzená a uzavřená.")
    await reload()
    auth.refresh()
  } catch (error) {
    reportError(error)
  }
}
</script>

<template>
  <main v-if="data" class="page batch-page">
    <div class="crumb">
      <RouterLink
        :to="{ name: 'area', params: { id: data.area.id }, query: { batch: batch.id } }"
      >
        {{ data.area.name }}
      </RouterLink>
      <AppIcon name="chev" />
      <RouterLink :to="{ name: 'open_batches' }">Dávky</RouterLink>
    </div>
    <div class="row head">
      <div>
        <p class="eyebrow">Dávka kontrol · {{ data.area.name }}</p>
        <h1>{{ batch.name }}</h1>
        <p class="muted small">
          Vytvořena {{ formatDate(batch.created_at) }}
          <template v-if="batch.created_by">
            · {{ batch.created_by.first_name }} {{ batch.created_by.last_name }}
          </template>
          <template v-if="batch.confirmed_at">
            · potvrzeno {{ formatDate(batch.confirmed_at) }}
          </template>
        </p>
      </div>
    </div>
    <div class="card stack progress-card">
      <BatchProgress :batch="batch" />
      <BatchLink v-if="!batch.closed_at" :token="batch.token" />
    </div>

    <div class="tiles" data-testid="batch-tiles">
      <div
        v-for="tile in tiles"
        :key="tile.label"
        class="tile"
        :class="tile.value && tile.tone"
      >
        <b class="num">{{ tile.value }}</b>
        <span>{{ tile.label }}</span>
      </div>
    </div>

    <template v-if="highlights.length">
      <h2 class="section-heading">Na co se podívat</h2>
      <div class="highlights">
        <div v-for="item in highlights" :key="item.key" class="highlight">
          <MarkerGlyph
            :state="(item.check && reportedState(item.check)) ?? 'to_check'"
          />
          <RouterLink class="name" :to="{ name: 'box', params: { id: item.box.id } }">
            {{ item.box.name }}
          </RouterLink>
          <div class="text">
            <b>{{ item.title }}</b>
            <span v-if="item.detail" class="muted small detail">{{ item.detail }}</span>
          </div>
          <span class="tag" :class="item.tone">
            {{
              item.tone === "bad" ? "pozor" : item.tone === "warn" ? "údržba" : "změna"
            }}
          </span>
        </div>
      </div>
    </template>

    <h2 class="section-heading">Všechny kontroly</h2>
    <div class="scroll-x">
      <table class="tbl checks" data-testid="batch-checks">
        <thead>
          <tr>
            <th>Budka</th>
            <th>Datum</th>
            <th class="hide-sm">Nalezena</th>
            <th class="hide-sm">Vyčištěno</th>
            <th>Uvnitř</th>
            <th class="hide-sm">Stav</th>
            <th class="hide-sm">Změny</th>
            <th class="hide-sm">Foto</th>
            <th class="hide-sm">Kdo</th>
            <th />
          </tr>
        </thead>
        <tbody>
          <template v-for="check in checks" :key="check.id">
            <tr
              :class="{
                flagged:
                  check.found === 'not_found' ||
                  ['needs_repair', 'needs_replacing', 'taken_down'].includes(
                    check.box_left,
                  ),
                editing: editingId === check.id,
              }"
              :data-check-row="boxesById.get(check.box_id).name"
            >
              <td class="num">
                <b>{{ boxesById.get(check.box_id).name }}</b>
              </td>
              <td class="num">{{ formatDate(check.date) }}</td>
              <td class="hide-sm">{{ yesNo(check.found === "found") }}</td>
              <td class="hide-sm">{{ CLEANING_LABELS[check.cleaning] ?? "–" }}</td>
              <td>{{ checkResult(check, occupantsById) }}</td>
              <td class="hide-sm">{{ BOX_LEFT_LABELS[check.box_left] ?? "–" }}</td>
              <td class="hide-sm">
                <span v-if="Object.keys(check.box_changes).length" class="tag info">
                  {{ boxChangesLabel(check.box_changes, typesById) }}
                </span>
              </td>
              <td class="hide-sm">
                <span v-if="check.photos.length" class="thumbs">
                  <img
                    v-for="photo in check.photos"
                    :key="photo.id"
                    :src="photo.photo.small"
                    alt="Fotka z kontroly"
                  />
                </span>
              </td>
              <td class="hide-sm">{{ who(check) }}</td>
              <td class="row-actions">
                <span v-if="check.is_confirmed" class="tag ok">potvrzeno</span>
                <button
                  type="button"
                  class="edit"
                  :aria-label="`Upravit kontrolu ${boxesById.get(check.box_id).name}`"
                  @click="editingId = editingId === check.id ? null : check.id"
                >
                  <AppIcon :name="editingId === check.id ? 'x' : 'edit'" />
                </button>
              </td>
            </tr>
            <tr v-if="editingId === check.id" class="edit-row">
              <td colspan="10">
                <CheckForm
                  :box="boxesById.get(check.box_id)"
                  :initial="check"
                  :categories="data.categories"
                  :help-articles="data.helpArticles"
                  :submit="saveEdit"
                  editable-date
                  inline
                  save-label="Uložit úpravu"
                  @cancel="editingId = null"
                >
                  <template #actions>
                    <n-popconfirm @positive-click="remove(check)">
                      <template #trigger>
                        <n-button type="error" ghost>
                          <template #icon><AppIcon name="trash" /></template>
                          Smazat
                        </n-button>
                      </template>
                      Smazat tuhle kontrolu?
                    </n-popconfirm>
                  </template>
                </CheckForm>
              </td>
            </tr>
          </template>
          <tr v-if="!checks.length">
            <td colspan="10" class="muted">Zatím tu není žádná kontrola.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <section class="card stack add" data-testid="add-check">
      <div class="row">
        <h3>Přidat kontrolu</h3>
        <span class="small muted">třeba z papírového formuláře, řádek po řádku</span>
      </div>
      <n-select
        v-model:value="adding.boxId"
        :options="addOptions"
        filterable
        placeholder="Která budka"
        :input-props="{ 'aria-label': 'Budka nové kontroly' }"
        class="box-select"
      />
      <CheckForm
        v-if="addingBox"
        :key="`${adding.key}-${addingBox.id}`"
        :box="addingBox"
        :categories="data.categories"
        :help-articles="data.helpArticles"
        :submit="saveNew"
        :default-date="adding.date"
        editable-date
        inline
        save-label="Zapsat kontrolu"
        @cancel="adding.boxId = null"
      />
    </section>

    <div class="sticky-bar">
      <span>
        <b>{{ checkCountLabel(data.checks.length) }}</b>
        <span class="muted">
          ·
          {{
            batch.pending_count
              ? `${pendingLabel(batch.pending_count)} na potvrzení`
              : "vše potvrzeno"
          }}
        </span>
      </span>
      <span class="spacer" />
      <span v-if="!batch.closed_at" class="small muted hide-sm">
        Po potvrzení odkaz přestane přijímat kontroly.
      </span>
      <n-popconfirm v-if="!batch.confirmed_at" @positive-click="confirm">
        <template #trigger>
          <n-button type="primary" size="large">
            <template #icon><AppIcon name="check" /></template>
            Potvrdit a uzavřít
          </n-button>
        </template>
        Potvrdit všechny čekající kontroly a nové budky? Zapíšou se do budek a dávka se
        uzavře.
      </n-popconfirm>
      <span v-else class="tag ok">potvrzená {{ formatDate(batch.confirmed_at) }}</span>
    </div>
  </main>
  <main v-else class="page"><p class="muted">Načítám…</p></main>
</template>

<style scoped>
.batch-page {
  max-width: 1180px;
  gap: 20px;
  padding-bottom: 0;
}

.head h1 {
  margin-top: 6px;
}

.head .small {
  margin-top: 6px;
}

.tiles {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
  gap: 10px;
}

.tile {
  display: grid;
  gap: 2px;
  padding: 14px 16px;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--r);
}

.tile b {
  font-size: 26px;
  font-weight: 800;
  line-height: 1.05;
}

.tile span {
  font-size: 13px;
  color: var(--muted);
}

.tile.warn {
  background: var(--warn-soft);
  border-color: transparent;
}

.tile.warn b {
  color: var(--warn);
}

.tile.bad {
  background: var(--danger-soft);
  border-color: transparent;
}

.tile.bad b {
  color: var(--danger);
}

.highlights {
  display: grid;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--r);
}

.highlight {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
}

.highlight + .highlight {
  border-top: 1px solid var(--line);
}

.highlight .name {
  font-weight: 800;
  min-width: 52px;
  color: var(--text);
}

.highlight .detail {
  margin-left: 6px;
}

.highlight .text {
  flex: 1;
  min-width: 0;
}

.checks tr.flagged td {
  background: var(--warn-soft);
}

.checks tr.editing td {
  background: var(--primary-soft);
}

.edit-row td {
  padding: 16px;
  background: var(--surface-2);
}

.row-actions {
  white-space: nowrap;
  text-align: right;
}

.edit {
  width: 32px;
  height: 32px;
  margin-left: 6px;
  border-radius: var(--r-btn);
  border: 1px solid var(--line-strong);
  background: var(--surface);
  color: var(--text);
  display: inline-grid;
  place-items: center;
  cursor: pointer;
  vertical-align: middle;
}

.edit .icon {
  width: 16px;
  height: 16px;
}

.thumbs {
  display: flex;
  gap: 4px;
}

.thumbs img {
  width: 30px;
  height: 30px;
  object-fit: cover;
  border-radius: 5px;
}

.box-select {
  max-width: 320px;
}

.sticky-bar {
  position: sticky;
  bottom: 0;
  z-index: 3;
  display: flex;
  align-items: center;
  gap: 14px;
  flex-wrap: wrap;
  margin: 0 -32px;
  padding: 14px 32px;
  background: var(--surface);
  border-top: 1px solid var(--line);
  box-shadow: 0 -4px 18px var(--shadow-c);
}

@media (max-width: 720px) {
  .sticky-bar {
    margin: 0 -16px;
    padding: 12px 16px;
  }
}
</style>
