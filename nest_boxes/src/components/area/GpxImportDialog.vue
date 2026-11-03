<script setup>
import { computed, ref, watch } from "vue"
import { NButton, NCheckbox, NDatePicker, NModal, NSelect } from "naive-ui"

import AppIcon from "@/components/app/AppIcon.vue"
import { formatDistance } from "@/composables/czech.js"
import { categoryOptions } from "@/composables/labels.js"
import { reportError } from "@/data/errors.js"
import { importGpx } from "@/data/manage.js"

const props = defineProps({
  areaId: { type: Number, required: true },
  types: { type: Array, required: true },
})

const emit = defineEmits(["imported"])
const show = defineModel("show", { type: Boolean, required: true })

const ACTIONS = {
  new: { label: "nová", tone: "ok" },
  move: { label: "posunout", tone: "info" },
  unchanged: { label: "beze změny", tone: "" },
  ambiguous: { label: "víc budek se jménem", tone: "warn" },
}
const APPLIED = ["new", "move"]

const gpx = ref("")
const fileName = ref("")
const typeId = ref(null)
const installedOn = ref(null)
const rows = ref(null)
const skip = ref([])
const loading = ref(false)

watch(show, open => {
  if (!open) return
  gpx.value = ""
  fileName.value = ""
  rows.value = null
  skip.value = []
})

const typeOptions = computed(() => categoryOptions(props.types))
const applied = computed(
  () =>
    rows.value?.filter(
      (row, index) => APPLIED.includes(row.action) && !skip.value.includes(index),
    ).length ?? 0,
)

const onFile = async event => {
  const [file] = event.target.files
  fileName.value = file.name
  gpx.value = await file.text()
  rows.value = null
}

const send = apply =>
  importGpx(props.areaId, {
    gpx: gpx.value,
    type_id: typeId.value,
    installed_on: installedOn.value,
    apply,
    skip: skip.value,
  })

const review = async () => {
  loading.value = true
  try {
    rows.value = (await send(false)).rows
    // Rows close to another row are often the same box twice
    skip.value = rows.value.flatMap((row, index) =>
      row.close_rows.some(other => other < index) ? [index] : [],
    )
  } catch (error) {
    reportError(error)
  } finally {
    loading.value = false
  }
}

const apply = async () => {
  loading.value = true
  try {
    await send(true)
    show.value = false
    emit("imported", applied.value)
  } catch (error) {
    reportError(error)
  } finally {
    loading.value = false
  }
}

const toggle = (index, included) =>
  (skip.value = included
    ? skip.value.filter(other => other !== index)
    : [...skip.value, index])
</script>

<template>
  <n-modal
    v-model:show="show"
    preset="card"
    title="Import z GPX"
    :style="{ width: 'min(760px, calc(100vw - 24px))' }"
  >
    <div class="stack">
      <p class="small muted">
        Body se párují s budkami oblasti podle označení. Nové body se založí jako
        vyvěšené neověřené budky, u známých se změní poloha. Nejdřív uvidíš, co se
        stane.
      </p>
      <div class="row">
        <label class="file">
          <AppIcon name="up" />
          {{ fileName || "Vybrat soubor GPX" }}
          <input
            type="file"
            accept=".gpx,application/gpx+xml"
            hidden
            @change="onFile"
          />
        </label>
      </div>
      <div class="grid-2">
        <div class="field">
          <span class="label">Typ nových budek</span>
          <n-select
            v-model:value="typeId"
            :options="typeOptions"
            clearable
            placeholder="Nevím"
          />
        </div>
        <div class="field">
          <span class="label">Vyvěšené dne</span>
          <n-date-picker
            v-model:formatted-value="installedOn"
            value-format="yyyy-MM-dd"
            format="d. M. yyyy"
            type="date"
            clearable
          />
        </div>
      </div>
      <div v-if="rows" class="scroll-x">
        <table class="tbl" data-testid="gpx-rows">
          <thead>
            <tr>
              <th />
              <th>Označení</th>
              <th>Co se stane</th>
              <th>Upozornění</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, index) in rows" :key="index">
              <td>
                <n-checkbox
                  v-if="APPLIED.includes(row.action)"
                  :checked="!skip.includes(index)"
                  @update:checked="toggle(index, $event)"
                />
              </td>
              <td>
                <b>{{ row.name }}</b>
              </td>
              <td>
                <span class="tag" :class="ACTIONS[row.action].tone">
                  {{ ACTIONS[row.action].label }}
                  <template v-if="row.action === 'move'">
                    o {{ formatDistance(row.moved_by) }}
                  </template>
                </span>
              </td>
              <td class="small">
                <div v-for="warning in row.warnings" :key="warning.box_id">
                  {{ formatDistance(warning.distance) }} od {{ warning.box_name }}
                </div>
                <div v-if="row.close_rows.length" class="muted">
                  blízko řádků
                  {{ row.close_rows.map(other => rows[other].name).join(", ") }}
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <template #footer>
      <div class="row">
        <n-button
          v-if="!rows"
          type="primary"
          :disabled="!gpx"
          :loading="loading"
          @click="review"
        >
          Ukázat, co se stane
        </n-button>
        <n-button
          v-else
          type="primary"
          :disabled="!applied"
          :loading="loading"
          @click="apply"
        >
          Importovat {{ applied }}
        </n-button>
        <n-button @click="show = false">Zrušit</n-button>
      </div>
    </template>
  </n-modal>
</template>

<style scoped>
.file {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  border: 1px dashed var(--line-strong);
  border-radius: var(--r-btn);
  cursor: pointer;
  font-weight: 700;
}
</style>
