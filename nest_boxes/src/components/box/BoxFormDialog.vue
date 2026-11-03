<script setup>
import { computed, ref, watch } from "vue"
import { watchDebounced } from "@vueuse/core"
import { NButton, NInput, NInputNumber, NModal, NSelect, NSwitch } from "naive-ui"

import AppIcon from "@/components/app/AppIcon.vue"
import ChoiceChips from "@/components/app/ChoiceChips.vue"
import BoxFields from "@/components/box/BoxFields.vue"
import { boxValues } from "@/components/check/checkForm.js"
import { formatDistance } from "@/composables/czech.js"
import {
  CONDITION_OPTIONS,
  EDITABLE_STATUSES,
  STATUS_LABELS,
} from "@/composables/labels.js"
import { reportError } from "@/data/errors.js"
import { createBox, getBoxWarnings, updateBox } from "@/data/manage.js"

const DEFAULT_PLAN_RADIUS = 20

const props = defineProps({
  // the box to edit, or null to plan a new one
  box: { type: Object, default: null },
  areaId: { type: Number, required: true },
  // where the map starts for a new box
  center: { type: Object, required: true },
  // a new box is planned into this batch
  batchId: { type: Number, default: null },
  types: { type: Array, required: true },
})

const emit = defineEmits(["saved"])
const show = defineModel("show", { type: Boolean, required: true })

const blank = () => ({
  name: "",
  hole_shape: "",
  hole_size: null,
  type: null,
  opening: "",
  material: "",
  location: null,
  installed_on: null,
})

const fieldsOf = box =>
  box
    ? {
        ...boxValues(box),
        status: box.status,
        condition: box.condition,
        planned_radius: box.planned_radius,
        predator_guard: box.predator_guard,
        previous_names: box.previous_names,
        access_note: box.access_note,
        owner_note: box.owner_note,
        note: box.note,
      }
    : {
        ...blank(),
        status: "planned",
        condition: "fine",
        planned_radius: DEFAULT_PLAN_RADIUS,
        predator_guard: null,
        previous_names: "",
        access_note: "",
        owner_note: "",
        note: "",
      }

const values = ref(fieldsOf(props.box))
const errors = ref({})
const warnings = ref({ spacing: [], duplicate_names: [] })
const saving = ref(false)

watch(show, open => {
  if (!open) return
  values.value = fieldsOf(props.box)
  errors.value = {}
})

const planned = computed(() => values.value.status === "planned")
const statusOptions = computed(() =>
  EDITABLE_STATUSES.filter(
    status => status !== "planned" || !props.box || props.box.status === "planned",
  ).map(value => ({ value, label: STATUS_LABELS[value] })),
)
const boxFields = computed({
  get: () => values.value,
  set: changed => (values.value = { ...values.value, ...changed }),
})

watchDebounced(
  () => [values.value.location, values.value.type, values.value.name],
  async ([location, type, name]) => {
    if (!show.value) return
    try {
      warnings.value = await getBoxWarnings({
        area: props.areaId,
        location,
        type,
        name,
        exclude: props.box?.id,
      })
    } catch (error) {
      reportError(error)
    }
  },
  { debounce: 400 },
)

const payload = () => {
  const { type, ...rest } = values.value
  return {
    ...rest,
    type_id: type,
    planned_radius: planned.value ? rest.planned_radius : null,
    area_id: props.areaId,
    ...(!props.box && props.batchId && { batch_id: props.batchId }),
  }
}

const save = async () => {
  errors.value = {
    ...(!values.value.name && { name: "Zadej označení." }),
    ...(!values.value.location && { location: "Klepni do mapy, kam budka patří." }),
  }
  if (Object.keys(errors.value).length) return
  saving.value = true
  try {
    const saved = props.box
      ? await updateBox(props.box.id, payload())
      : await createBox(payload())
    show.value = false
    emit("saved", saved)
  } catch (error) {
    reportError(error)
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <n-modal
    v-model:show="show"
    preset="card"
    :title="box ? `Úprava budky ${box.name}` : 'Naplánovat budku'"
    class="box-dialog"
    :style="{ width: 'min(720px, calc(100vw - 24px))' }"
    :mask-closable="false"
  >
    <div class="stack">
      <p v-if="!box" class="muted small">
        Dobrovolníci uvidí kroužek, kam budku pověsit. Pověšení zapíšou kontrolou se
        skutečnou polohou.
      </p>
      <div class="grid-2">
        <div class="field">
          <span class="label">Stav</span>
          <n-select v-model:value="values.status" :options="statusOptions" />
        </div>
        <div v-if="planned" class="field">
          <label for="box-radius">Okruh, kam ji pověsit</label>
          <n-input-number
            v-model:value="values.planned_radius"
            :input-props="{ id: 'box-radius' }"
            :min="1"
            :max="2000"
          >
            <template #suffix>m</template>
          </n-input-number>
        </div>
        <div v-else class="field">
          <span class="label">Stav budky</span>
          <ChoiceChips v-model="values.condition" :options="CONDITION_OPTIONS" />
        </div>
      </div>
      <BoxFields
        v-model="boxFields"
        :types="types"
        :center="box?.location ?? center"
        :errors="errors"
        :fields="
          planned
            ? [
                'name',
                'location',
                'hole_shape',
                'hole_size',
                'type',
                'opening',
                'material',
              ]
            : undefined
        "
      />
      <div
        v-for="warning in warnings.spacing"
        :key="warning.box_id"
        class="note warn"
        data-testid="spacing-warning"
      >
        <AppIcon name="warn" />
        <div>
          <b>Blízko jiné budky</b>
          {{ warning.box_name }} visí {{ formatDistance(warning.distance) }} odsud{{
            warning.is_same_type ? " a je stejného typu" : ""
          }}. Budky dávej aspoň 15 m od jiných a 50 m od budek stejného typu.
        </div>
      </div>
      <div
        v-for="duplicate in warnings.duplicate_names"
        :key="duplicate.id"
        class="note warn"
      >
        <AppIcon name="warn" />
        <div>
          <b>Budka s tímto označením už existuje</b>
          V oblasti už visí jiná budka {{ duplicate.name }}.
        </div>
      </div>
      <div class="row">
        <span class="label">Ochrana proti predátorům</span>
        <n-switch
          :value="values.predator_guard === true"
          @update:value="values.predator_guard = $event"
        />
      </div>
      <div class="field">
        <label for="box-access">Jak se k budce dostat</label>
        <n-input
          v-model:value="values.access_note"
          type="textarea"
          :autosize="{ minRows: 1 }"
          :input-props="{ id: 'box-access' }"
        />
      </div>
      <div class="grid-2">
        <div class="field">
          <label for="box-owner-note">Poznámka k majiteli</label>
          <n-input
            v-model:value="values.owner_note"
            type="textarea"
            :autosize="{ minRows: 1 }"
            :input-props="{ id: 'box-owner-note' }"
          />
        </div>
        <div class="field">
          <label for="box-previous">Dřívější označení</label>
          <n-input
            v-model:value="values.previous_names"
            :input-props="{ id: 'box-previous' }"
          />
        </div>
      </div>
      <div class="field">
        <label for="box-note">Poznámka</label>
        <n-input
          v-model:value="values.note"
          type="textarea"
          :autosize="{ minRows: 2 }"
          :input-props="{ id: 'box-note' }"
        />
      </div>
    </div>
    <template #footer>
      <div class="row">
        <n-button type="primary" :loading="saving" @click="save">
          {{ box ? "Uložit budku" : "Naplánovat" }}
        </n-button>
        <n-button @click="show = false">Zrušit</n-button>
      </div>
    </template>
  </n-modal>
</template>
