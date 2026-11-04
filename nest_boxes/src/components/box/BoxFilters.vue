<script setup>
import { computed } from "vue"
import { NInput, NPopselect } from "naive-ui"

import AppIcon from "@/components/app/AppIcon.vue"
import { CHECKED_OPTIONS } from "@/composables/areaBoxes.js"
import {
  categoryOptions,
  SEASON_STATE_LABELS,
  SEASON_STATE_OPTIONS,
  STATUS_OPTIONS,
} from "@/composables/labels.js"

const props = defineProps({
  types: { type: Array, required: true },
  unverifiedCount: { type: Number, required: true },
})

// see defaultFilters in composables/areaBoxes.js
const filters = defineModel({ type: Object, required: true })

const typeOptions = computed(() => categoryOptions(props.types))
</script>

<template>
  <div class="chips">
    <n-popselect
      v-model:value="filters.type"
      :options="typeOptions"
      multiple
      trigger="click"
      scrollable
    >
      <button type="button" class="chip" :class="{ on: filters.type.length }">
        <AppIcon name="filter" />Typ<template v-if="filters.type.length">
          {{ filters.type.length }}</template
        >
      </button>
    </n-popselect>
    <n-popselect
      v-model:value="filters.state"
      :options="SEASON_STATE_OPTIONS"
      multiple
      trigger="click"
    >
      <button type="button" class="chip" :class="{ on: filters.state.length }">
        {{
          filters.state.length === 1
            ? SEASON_STATE_LABELS[filters.state[0]]
            : `Letošní stav${filters.state.length ? ` ${filters.state.length}` : ""}`
        }}
        <AppIcon name="chevd" />
      </button>
    </n-popselect>
    <n-popselect
      v-model:value="filters.status"
      :options="STATUS_OPTIONS"
      multiple
      trigger="click"
    >
      <button type="button" class="chip">
        Stav {{ filters.status.length }}
        <AppIcon name="chevd" />
      </button>
    </n-popselect>
    <button
      type="button"
      class="chip"
      :class="{ on: filters.unverified }"
      @click="filters.unverified = !filters.unverified"
    >
      Neověřené {{ unverifiedCount }}
    </button>
    <n-popselect
      v-model:value="filters.checked"
      :options="CHECKED_OPTIONS"
      trigger="click"
    >
      <button type="button" class="chip" :class="{ on: filters.checked }">
        {{
          CHECKED_OPTIONS.find(option => option.value === filters.checked)?.label ??
          "Kontrola"
        }}
        <AppIcon name="chevd" />
      </button>
    </n-popselect>
    <button
      v-if="filters.checked"
      type="button"
      class="chip dim"
      aria-label="Zrušit filtr kontroly"
      @click="filters.checked = null"
    >
      <AppIcon name="x" />
    </button>
  </div>
  <n-input
    v-model:value="filters.search"
    size="small"
    clearable
    placeholder="Hledat označení"
  />
</template>
