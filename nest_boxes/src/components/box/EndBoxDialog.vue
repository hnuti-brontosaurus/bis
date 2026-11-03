<script setup>
import { computed, ref } from "vue"
import { NButton, NDatePicker, NModal } from "naive-ui"

import ChoiceChips from "@/components/app/ChoiceChips.vue"
import { isoDate } from "@/composables/czech.js"
import { categoryOptions } from "@/composables/labels.js"
import { reportError } from "@/data/errors.js"
import { endBox } from "@/data/manage.js"

const props = defineProps({
  box: { type: Object, required: true },
  endReasons: { type: Array, required: true },
})

const emit = defineEmits(["ended"])
const show = defineModel("show", { type: Boolean, required: true })

const reasonId = ref(null)
const endedOn = ref(isoDate())
const saving = ref(false)

const reasonOptions = computed(() => categoryOptions(props.endReasons))

const end = async () => {
  saving.value = true
  try {
    const box = await endBox(props.box.id, {
      end_reason_id: reasonId.value,
      ended_on: endedOn.value,
    })
    show.value = false
    emit("ended", box)
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
    :title="`Ukončit budku ${box.name}`"
    :style="{ width: 'min(520px, calc(100vw - 24px))' }"
  >
    <div class="stack">
      <p class="small muted">
        Ukončenou budku nejde obnovit. Když místo ní visí nová, založ ji jako novou
        budku.
      </p>
      <div class="field">
        <span class="label">Proč</span>
        <ChoiceChips v-model="reasonId" :options="reasonOptions" />
      </div>
      <div class="field">
        <label for="end-date">Kdy</label>
        <n-date-picker
          v-model:formatted-value="endedOn"
          value-format="yyyy-MM-dd"
          format="d. M. yyyy"
          type="date"
          :input-props="{ id: 'end-date' }"
        />
      </div>
    </div>
    <template #footer>
      <div class="row">
        <n-button
          type="error"
          :disabled="!reasonId || !endedOn"
          :loading="saving"
          @click="end"
        >
          Ukončit budku
        </n-button>
        <n-button @click="show = false">Zrušit</n-button>
      </div>
    </template>
  </n-modal>
</template>
