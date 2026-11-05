<script setup>
import { NModal, NCard, NFlex, NSelect, NText } from "naive-ui"
import { computed } from "vue"
import { useUnitsStore } from "@/data/units.js"
import {
  convertAmount,
  convertibleUnits,
  pluralizeUnit,
  roundAmount,
} from "@/data/unitConversion.js"

const props = defineProps({
  row: { type: Object, default: null },
  amount: { type: Number, default: null },
})
const show = defineModel("show", { type: Boolean, default: false })
const unitId = defineModel("unitId", { type: Number, default: null })

const unitsStore = useUnitsStore()

const targetUnit = computed(() => unitsStore.byId[unitId.value] ?? props.row?.unit)

const converted = computed(() =>
  roundAmount(
    convertAmount(
      props.amount,
      props.row?.unit,
      targetUnit.value,
      props.row?.ingredient,
    ),
  ),
)

const options = computed(() =>
  props.row
    ? convertibleUnits(unitsStore.list, props.row).map(unit => ({
        label: pluralizeUnit(converted.value, unit),
        value: unit.id,
      }))
    : [],
)

const original = computed(() => roundAmount(props.amount))
</script>

<template>
  <n-modal v-model:show="show">
    <n-card
      :title="row.ingredient?.name"
      :bordered="false"
      closable
      role="dialog"
      style="max-width: 360px; width: 90vw"
      @close="show = false"
    >
      <n-flex vertical :size="16">
        <n-text depth="3">
          {{ original }} {{ pluralizeUnit(original, row.unit) }} =
        </n-text>
        <n-flex align="center" :wrap="false">
          <span class="converted display-font">{{ converted ?? "–" }}</span>
          <n-select
            :value="targetUnit?.id"
            @update:value="value => (unitId = value)"
            :options="options"
            :consistent-menu-width="false"
            style="flex: 1"
          />
        </n-flex>
      </n-flex>
    </n-card>
  </n-modal>
</template>

<style scoped>
.converted {
  font-size: 1.6em;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}
</style>
