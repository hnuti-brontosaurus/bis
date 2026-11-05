<script setup>
import { computed, ref, shallowRef, watch } from "vue"
import { NButton, NInput, NModal, NSelect } from "naive-ui"

import { reportError } from "@/data/errors.js"
import { createArea, listUnits, updateArea } from "@/data/manage.js"

const props = defineProps({
  // the area to edit, or null for a new one
  area: { type: Object, default: null },
})

const emit = defineEmits(["saved"])
const show = defineModel("show", { type: Boolean, required: true })

const units = shallowRef([])
const values = ref({})
const saving = ref(false)
const error = ref("")

const unitOptions = computed(() =>
  units.value.map(unit => ({ value: unit.id, label: unit.abbreviation })),
)

watch(
  show,
  open => {
    if (!open) return
    values.value = {
      name: props.area?.name ?? "",
      administration_unit_id: props.area?.administration_unit_id ?? null,
      note: props.area?.note ?? "",
    }
    error.value = ""
    if (!units.value.length)
      listUnits().then(result => (units.value = result), reportError)
  },
  { immediate: true },
)

const save = async () => {
  if (!values.value.name || !values.value.administration_unit_id) {
    error.value = "Oblast potřebuje název a článek, který se o ni stará."
    return
  }
  saving.value = true
  try {
    const saved = props.area
      ? await updateArea(props.area.id, values.value)
      : await createArea(values.value)
    show.value = false
    emit("saved", saved)
  } catch (failure) {
    reportError(failure)
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <n-modal
    v-model:show="show"
    preset="card"
    :title="area ? 'Úprava oblasti' : 'Nová oblast'"
    :style="{ width: 'min(520px, calc(100vw - 24px))' }"
  >
    <div class="stack">
      <div class="field">
        <label for="area-name">Název</label>
        <n-input
          v-model:value="values.name"
          :maxlength="127"
          :input-props="{ id: 'area-name' }"
        />
      </div>
      <div class="field">
        <label for="area-unit">Stará se o ni</label>
        <n-select
          v-model:value="values.administration_unit_id"
          :options="unitOptions"
          :input-props="{ id: 'area-unit' }"
          filterable
          placeholder="Základní článek"
        />
      </div>
      <div class="field">
        <label for="area-note">Poznámka</label>
        <n-input
          v-model:value="values.note"
          type="textarea"
          :autosize="{ minRows: 2 }"
          :input-props="{ id: 'area-note' }"
        />
      </div>
      <span v-if="error" class="error">{{ error }}</span>
    </div>
    <template #footer>
      <div class="row">
        <n-button type="primary" :loading="saving" @click="save">Uložit</n-button>
        <n-button @click="show = false">Zrušit</n-button>
      </div>
    </template>
  </n-modal>
</template>

<style scoped>
.error {
  color: var(--danger);
  font-weight: 700;
  font-size: 13px;
}
</style>
