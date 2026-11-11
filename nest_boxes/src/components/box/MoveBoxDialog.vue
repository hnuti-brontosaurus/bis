<script setup>
import { computed, ref } from "vue"
import { NButton, NModal, useMessage } from "naive-ui"

import AreaSelect from "@/components/area/AreaSelect.vue"
import { boxCountLabel } from "@/composables/czech.js"
import { reportError } from "@/data/errors.js"
import { moveBoxes } from "@/data/manage.js"

const props = defineProps({
  boxes: { type: Array, required: true },
})

const emit = defineEmits(["close", "moved"])

const message = useMessage()
const show = ref(true)
const areaIds = new Set(props.boxes.map(box => box.area_id))
// Preselected when they all share one, so a single box shows where it is
const areaId = ref(areaIds.size === 1 ? props.boxes[0].area_id : null)
const saving = ref(false)

const title = computed(() =>
  props.boxes.length === 1
    ? `Přesunout budku ${props.boxes[0].name}`
    : `Přesunout ${boxCountLabel(props.boxes.length)}`,
)
const unchanged = computed(() => areaIds.size === 1 && areaIds.has(areaId.value))

const move = async () => {
  saving.value = true
  try {
    const { boxes, duplicate_names } = await moveBoxes(
      props.boxes.map(box => box.id),
      areaId.value,
    )
    message.success(
      boxes.length === 1
        ? `Budka ${boxes[0].name} je přesunutá.`
        : `Přesunuto: ${boxCountLabel(boxes.length)}.`,
    )
    if (duplicate_names.length)
      message.warning(
        `V nové oblasti už visí jiné budky se stejným označením: ${duplicate_names.join(", ")}.`,
      )
    emit("moved", boxes)
    show.value = false
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
    :title="title"
    :style="{ width: 'min(440px, calc(100vw - 24px))' }"
    @after-leave="emit('close')"
  >
    <div class="stack">
      <div class="field">
        <label for="move-area">Do oblasti</label>
        <AreaSelect id="move-area" v-model="areaId" />
      </div>
      <p class="small muted">
        Budky zůstanou, kde visí, i se svými kontrolami. Z otevřených obchůzek dosavadní
        oblasti vypadnou.
      </p>
    </div>
    <template #footer>
      <div class="row">
        <n-button
          type="primary"
          :loading="saving"
          :disabled="!areaId || unchanged"
          @click="move"
        >
          Přesunout
        </n-button>
        <n-button @click="show = false">Zrušit</n-button>
      </div>
    </template>
  </n-modal>
</template>
