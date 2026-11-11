<script setup>
import { computed, shallowRef } from "vue"
import { NSelect } from "naive-ui"

import { reportError } from "@/data/errors.js"
import { listAreas } from "@/data/manage.js"

defineProps({ id: { type: String, required: true } })

const value = defineModel({ type: Number, default: null })

// Only the areas the user manages, which are the only ones a box may go to
const areas = shallowRef(null)
listAreas().then(result => (areas.value = result), reportError)

const options = computed(() =>
  (areas.value ?? []).map(area => ({
    value: area.id,
    label: `${area.name} · ${area.administration_unit.abbreviation}`,
  })),
)
</script>

<template>
  <n-select
    v-model:value="value"
    :options="options"
    :loading="!areas"
    :input-props="{ id }"
    filterable
  />
</template>
