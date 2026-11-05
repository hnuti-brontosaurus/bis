<script setup>
import { computed, ref } from "vue"
import { NButton, NCheckbox, NInput, NModal, NSelect } from "naive-ui"

import AppIcon from "@/components/app/AppIcon.vue"
import ChoiceChips from "@/components/app/ChoiceChips.vue"
import MarkerGlyph from "@/components/map/MarkerGlyph.vue"
import {
  CHECKED_OPTIONS,
  defaultFilters,
  isDefaultShown,
  LEGEND_KEYS,
} from "@/composables/filters.js"
import { categoryOptions, LEGEND_LABELS } from "@/composables/labels.js"

const props = defineProps({
  // see defaultFilters in composables/filters.js
  filters: { type: Object, required: true },
  // [{ label, value }] of administration units; null where there is just one
  units: { type: Array, default: null },
  types: { type: Array, required: true },
  // filter key → why it doesn't apply to what the map shows now
  unavailable: { type: Object, default: () => ({}) },
  // null where the filter is not offered at all
  unverifiedCount: { type: Number, default: null },
  checked: { type: Boolean, default: true },
  searchPlaceholder: { type: String, required: true },
  // legend key → count; null hides the legend
  legendCounts: { type: Object, default: null },
  // the part of the map under the phone's bottom sheet
  bottomInset: { type: Number, default: 0 },
  // the phone sheet's stop, see SHEET_STOPS; null on a desktop
  sheetStop: { type: String, default: null },
})

const emit = defineEmits(["update"])

const update = patch => emit("update", patch)

const open = ref(false)
const CHECKED_CHOICES = [{ value: null, label: "Kdykoli" }, ...CHECKED_OPTIONS]

const typeOptions = computed(() => categoryOptions(props.types))
const typesById = computed(() => new Map(props.types.map(type => [type.id, type])))
const legendEntries = computed(() =>
  // A state no box is in would only take room; counted without the legend's own filter
  LEGEND_KEYS.filter(key => props.legendCounts?.[key]).map(key => ({
    key,
    label: LEGEND_LABELS[key],
    count: props.legendCounts[key],
    shown: props.filters.shown.includes(key),
  })),
)

const lower = key => LEGEND_LABELS[key].toLowerCase()
const listed = keys => keys.map(lower).join(", ")

const legendChip = computed(() => {
  const { shown } = props.filters
  if (shown.length <= 2) return shown.length ? `Jen ${listed(shown)}` : "Žádný stav"
  const hidden = LEGEND_KEYS.filter(key => key !== "ended" && !shown.includes(key))
  const parts = [
    ...(hidden.length ? [`bez ${listed(hidden)}`] : []),
    ...(shown.includes("ended") ? ["se zaniklými"] : []),
  ]
  const text = parts.join(", ")
  return text.charAt(0).toUpperCase() + text.slice(1)
})

const chips = computed(() => {
  const { filters } = props
  return [
    props.units &&
      filters.unit !== null && {
        key: "unit",
        label:
          props.units?.find(unit => unit.value === filters.unit)?.label ?? "Jednotka",
        reset: { unit: null },
      },
    filters.type.length && {
      key: "type",
      label:
        filters.type.length === 1
          ? `Typ: ${typesById.value.get(filters.type[0])?.name ?? "?"}`
          : `Typy: ${filters.type.length}`,
      reset: { type: [] },
    },
    !isDefaultShown(filters.shown) && {
      key: "shown",
      label: legendChip.value,
      reset: { shown: defaultFilters().shown },
    },
    props.unverifiedCount !== null &&
      filters.unverified && {
        key: "unverified",
        label: "Neověřené",
        reset: { unverified: false },
      },
    props.checked &&
      filters.checked && {
        key: "checked",
        label: CHECKED_OPTIONS.find(option => option.value === filters.checked).label,
        reset: { checked: null },
      },
  ].filter(Boolean)
})
// Only what this map offers; a unit kept from the map of areas is no filter on one area
const count = computed(() => chips.value.length)

const resetAll = () => update({ ...defaultFilters(), search: props.filters.search })

const toggle = key =>
  update({
    shown: props.filters.shown.includes(key)
      ? props.filters.shown.filter(item => item !== key)
      : [...props.filters.shown, key],
  })

const only = key => update({ shown: [key] })
</script>

<template>
  <div class="map-filters" :style="{ '--bottom-inset': `${bottomInset}px` }">
    <div v-show="sheetStop !== 'full'" class="top">
      <div class="bar">
        <div v-if="$slots.mode" class="mode"><slot name="mode" /></div>
        <n-input
          class="search"
          :value="filters.search"
          size="small"
          clearable
          :placeholder="searchPlaceholder"
          @update:value="update({ search: $event })"
        />
        <n-button size="small" data-testid="filters-button" @click="open = true">
          <template #icon><AppIcon name="filter" /></template>
          Filtry
          <span v-if="count" class="count">{{ count }}</span>
        </n-button>
      </div>
      <div v-if="chips.length" class="chips active hide-sm">
        <button
          v-for="chip in chips"
          :key="chip.key"
          type="button"
          class="chip on"
          :class="{ unavailable: unavailable[chip.key] }"
          :title="unavailable[chip.key]"
          :aria-label="`Zrušit filtr ${chip.label}`"
          @click="update(chip.reset)"
        >
          {{ chip.label }}<AppIcon name="x" />
        </button>
        <button type="button" class="chip dim" @click="resetAll">Zrušit vše</button>
      </div>
    </div>
    <div
      v-if="legendCounts"
      v-show="!sheetStop || sheetStop === 'collapsed'"
      class="legend"
      role="group"
      aria-label="Legenda, kliknutím skryješ nebo ukážeš"
      data-testid="legend"
    >
      <button
        v-for="entry in legendEntries"
        :key="entry.key"
        type="button"
        :class="{ off: !entry.shown }"
        :aria-pressed="entry.shown"
        :aria-label="`${entry.label} ${entry.count}`"
        :title="`${entry.label}: kliknutím ${entry.shown ? 'skryješ' : 'ukážeš'}, dvojklikem necháš jen ty`"
        @click="toggle(entry.key)"
        @dblclick="only(entry.key)"
      >
        <MarkerGlyph :state="entry.key === 'ended' ? 'out' : entry.key" />
        <span class="name hide-sm">{{ entry.label }}</span>
        <span class="num">{{ entry.count }}</span>
      </button>
    </div>
    <n-modal
      v-model:show="open"
      preset="card"
      title="Filtry"
      class="filters-modal"
      :bordered="false"
      data-testid="filters"
    >
      <div class="sections">
        <section :class="{ unavailable: unavailable.shown }">
          <h3>Stav</h3>
          <ChoiceChips
            v-if="legendEntries.length"
            :model-value="filters.shown"
            :options="legendEntries.map(entry => ({ ...entry, value: entry.key }))"
            multiple
            @update:model-value="update({ shown: $event })"
          >
            <template #option="{ option }">
              <MarkerGlyph :state="option.key === 'ended' ? 'out' : option.key" />
              {{ option.label }} <span class="muted num">{{ option.count }}</span>
            </template>
          </ChoiceChips>
          <p class="why">
            {{
              unavailable.shown ??
              "Stejně jako kliknutí na legendu v mapě. Zaniklé budky jsou zprvu skryté."
            }}
          </p>
        </section>
        <section v-if="units">
          <h3>Jednotka</h3>
          <n-select
            :value="filters.unit"
            :options="units"
            placeholder="Všechny jednotky"
            clearable
            @update:value="update({ unit: $event })"
          />
        </section>
        <section :class="{ unavailable: unavailable.type }">
          <h3>Typ budky</h3>
          <ChoiceChips
            :model-value="filters.type"
            :options="typeOptions"
            multiple
            @update:model-value="update({ type: $event })"
          />
          <p class="why">
            {{ unavailable.type ?? "Bez výběru všechny typy." }}
          </p>
        </section>
        <section v-if="checked" :class="{ unavailable: unavailable.checked }">
          <h3>Poslední kontrola</h3>
          <ChoiceChips
            :model-value="filters.checked"
            :options="CHECKED_CHOICES"
            @update:model-value="update({ checked: $event })"
          />
          <p v-if="unavailable.checked" class="why">{{ unavailable.checked }}</p>
        </section>
        <section
          v-if="unverifiedCount !== null"
          :class="{ unavailable: unavailable.unverified }"
        >
          <h3>Ověření</h3>
          <n-checkbox
            :checked="filters.unverified"
            @update:checked="update({ unverified: $event })"
          >
            Jen neověřené budky ({{ unverifiedCount }})
          </n-checkbox>
          <p class="why">
            {{
              unavailable.unverified ?? "Ověřená budka má potvrzenou kontrolu z terénu."
            }}
          </p>
        </section>
      </div>
      <template #footer>
        <div class="footer">
          <n-button quaternary :disabled="!count" @click="resetAll">
            Zrušit všechny filtry
          </n-button>
          <n-button type="primary" @click="open = false">Zavřít</n-button>
        </div>
      </template>
    </n-modal>
  </div>
</template>

<style scoped>
.map-filters {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 1;
}

.map-filters > * {
  pointer-events: auto;
}

.top {
  position: absolute;
  top: 10px;
  left: 10px;
  right: 60px;
  display: grid;
  justify-items: start;
  gap: 6px;
  pointer-events: none;
}

.top > * {
  pointer-events: auto;
}

.bar {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px;
  border-radius: 12px;
  background: var(--surface);
  box-shadow: 0 2px 10px var(--shadow-c);
  max-width: 100%;
}

.search {
  width: 210px;
}

.count {
  min-width: 18px;
  height: 18px;
  margin-left: 6px;
  padding: 0 5px;
  border-radius: 99px;
  background: var(--primary);
  color: var(--primary-ink);
  font-size: 11.5px;
  font-weight: 800;
  display: inline-grid;
  place-items: center;
}

.active .chip {
  box-shadow: 0 1px 4px var(--shadow-c);
  cursor: pointer;
}

.active .chip.dim {
  background: var(--surface);
}

.active .unavailable {
  opacity: 0.55;
}

.sections {
  display: grid;
  gap: 22px;
}

.sections section {
  display: grid;
  gap: 8px;
}

.sections h3 {
  margin: 0;
  font-size: 13px;
  font-weight: 800;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--muted);
}

.sections :deep(.marker-glyph) {
  width: 16px;
  height: 16px;
  border-width: 2.5px;
}

.sections :deep(.marker-glyph.out) {
  width: 12px;
  height: 12px;
}

.sections :deep(.marker-icon) {
  width: 11px;
  height: 11px;
}

.sections .num {
  font-weight: 600;
}

.why {
  margin: 0;
  font-size: 13px;
  color: var(--muted);
}

.unavailable > :not(h3, .why) {
  opacity: 0.5;
  pointer-events: none;
}

.footer {
  display: flex;
  justify-content: space-between;
  gap: 8px;
}

.legend {
  position: absolute;
  left: 10px;
  bottom: 10px;
  display: grid;
  gap: 2px;
  padding: 6px;
  border-radius: 12px;
  background: var(--surface);
  box-shadow: 0 2px 10px var(--shadow-c);
}

.legend button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 8px;
  border: 0;
  border-radius: 8px;
  background: none;
  color: var(--text);
  font: inherit;
  font-size: 13.5px;
  font-weight: 700;
  cursor: pointer;
  text-align: left;
  user-select: none;
}

.legend button:hover {
  background: var(--surface-2);
}

.legend button:focus-visible {
  outline: 2px solid var(--primary);
}

.legend .name {
  flex: 1;
}

.legend .num {
  color: var(--muted);
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}

.legend .off {
  opacity: 0.45;
}

.legend .off :deep(.marker-glyph) {
  filter: grayscale(1);
}

.legend :deep(.marker-glyph) {
  width: 18px;
  height: 18px;
  border-width: 2.5px;
}

.legend :deep(.marker-glyph.out) {
  width: 14px;
  height: 14px;
  margin: 2px;
}

.legend :deep(.marker-icon) {
  width: 12px;
  height: 12px;
}

@media (max-width: 720px) {
  .top {
    right: 56px;
    justify-items: stretch;
  }

  .bar {
    display: grid;
    grid-template-columns: minmax(0, 1fr) auto;
  }

  .mode {
    grid-column: 1 / -1;
    order: 1;
  }

  .search {
    width: auto;
  }

  .legend {
    left: 10px;
    right: 10px;
    bottom: calc(var(--bottom-inset) + 10px);
    display: flex;
    justify-content: space-between;
    padding: 4px;
  }

  .legend button {
    padding: 4px 6px;
    gap: 5px;
  }
}

@media (prefers-reduced-motion: no-preference) {
  .legend {
    transition: bottom 0.2s ease;
  }
}
</style>

<style>
/* n-modal renders in a portal, outside the scoped styles */
.filters-modal {
  width: min(560px, calc(100vw - 32px));
}
</style>
