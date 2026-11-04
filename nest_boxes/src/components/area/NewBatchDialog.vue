<script setup>
import { ref, watch } from "vue"
import { NButton, NInput, NModal } from "naive-ui"

import { reportError } from "@/data/errors.js"
import { createBatch, getSuggestedBoxes } from "@/data/manage.js"

const props = defineProps({
  areaId: { type: Number, required: true },
})

const emit = defineEmits(["created"])
const show = defineModel("show", { type: Boolean, required: true })

const AUTUMN_FROM_MONTH = 6

const defaultName = (today = new Date()) =>
  `${today.getMonth() >= AUTUMN_FROM_MONTH ? "Podzim" : "Jaro"} ${today.getFullYear()}`

const name = ref(defaultName())
const suggested = ref(null)
const saving = ref(false)

watch(
  show,
  open => {
    if (!open) return
    suggested.value = null
    getSuggestedBoxes(props.areaId).then(
      ({ box_ids }) => (suggested.value = box_ids.length),
      reportError,
    )
  },
  { immediate: true },
)

const create = async () => {
  saving.value = true
  try {
    const batch = await createBatch({ area_id: props.areaId, name: name.value })
    show.value = false
    emit("created", batch)
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
    title="Nová obchůzka"
    :style="{ width: 'min(480px, calc(100vw - 24px))' }"
  >
    <div class="stack">
      <div class="field">
        <label for="batch-name">Název</label>
        <n-input
          v-model:value="name"
          :maxlength="127"
          :input-props="{ id: 'batch-name' }"
        />
        <span class="hint"
          >Uvidí ho dobrovolníci, třeba „Podzim 2026 · skupina A“.</span
        >
      </div>
      <p class="small">
        <template v-if="suggested === null">Hledám budky…</template>
        <template v-else>
          Navržených budek: <b>{{ suggested }}</b
          >. Jsou to vyvěšené budky, které letos nikdo nezkontroloval a nejsou v jiné
          otevřené obchůzce. Další můžeš přidat nebo odebrat.
        </template>
      </p>
    </div>
    <template #footer>
      <div class="row">
        <n-button type="primary" :loading="saving" :disabled="!name" @click="create">
          Vytvořit obchůzku
        </n-button>
        <n-button @click="show = false">Zrušit</n-button>
      </div>
    </template>
  </n-modal>
</template>
