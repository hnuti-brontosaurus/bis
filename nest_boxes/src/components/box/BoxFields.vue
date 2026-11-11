<script setup>
import { computed, watch } from "vue"
import { NDatePicker, NInput, NInputNumber, NSelect } from "naive-ui"

import ChoiceChips from "@/components/app/ChoiceChips.vue"
import HelpBadge from "@/components/app/HelpBadge.vue"
import LocationPicker from "@/components/map/LocationPicker.vue"
import { suggestType, typeHint } from "@/components/check/checkForm.js"
import {
  categoryOptions,
  HOLE_SHAPE_OPTIONS,
  MATERIAL_OPTIONS,
  MEASURED_HOLE_SHAPES,
  OPENING_OPTIONS,
} from "@/composables/labels.js"

const props = defineProps({
  // NestBoxType[] from categories/
  types: { type: Array, required: true },
  // Where the location picker starts without a location
  center: { type: Object, required: true },
  errors: { type: Object, default: () => ({}) },
  // Which of the box_changes keys to show
  fields: {
    type: Array,
    default: () => [
      "name",
      "location",
      "hole_shape",
      "hole_size",
      "type",
      "opening",
      "material",
      "installed_on",
    ],
  },
  locateOnOpen: { type: Boolean, default: false },
})

defineEmits(["help"])

// { name, hole_shape, hole_size, type, opening, material, location, installed_on }
const values = defineModel({ type: Object, required: true })

const shows = name => props.fields.includes(name)
const typeOptions = computed(() => categoryOptions(props.types))
const measured = computed(() => MEASURED_HOLE_SHAPES.includes(values.value.hole_shape))
const selectedType = computed(() =>
  props.types.find(type => type.id === values.value.type),
)
const hint = computed(() =>
  typeHint(selectedType.value, values.value.hole_shape, values.value.hole_size),
)

const set = (name, value) => (values.value = { ...values.value, [name]: value })

// The type follows the hole until someone picks a type the hole doesn't suggest.
// Two sources, not one getter returning an array: a fresh array always counts
// as changed, so every set() would re-run this and set() again, forever.
watch(
  [() => values.value.hole_shape, () => values.value.hole_size],
  ([shape, size], [oldShape, oldSize]) => {
    const previous = suggestType(props.types, oldShape, oldSize)
    const next = suggestType(props.types, shape, size)
    const following = values.value.type === null || values.value.type === previous?.id
    if (next && following) set("type", next.id)
    if (!MEASURED_HOLE_SHAPES.includes(shape) && size !== null) set("hole_size", null)
  },
)
</script>

<template>
  <div class="box-fields">
    <div v-if="shows('name')" class="field">
      <label for="box-name">Označení</label>
      <n-input
        :input-props="{ id: 'box-name' }"
        :value="values.name"
        :maxlength="63"
        placeholder="Co je na budce napsané"
        @update:value="set('name', $event)"
      />
      <span v-if="errors.name" class="error">{{ errors.name }}</span>
    </div>
    <slot name="after-name" />
    <div v-if="shows('location')" class="field">
      <span class="label">Poloha</span>
      <LocationPicker
        :model-value="values.location"
        :center="center"
        :name="values.name"
        :locate-on-open="locateOnOpen"
        @update:model-value="set('location', $event)"
      >
        <slot name="map" />
      </LocationPicker>
      <span v-if="errors.location" class="error">{{ errors.location }}</span>
    </div>
    <div v-if="shows('hole_shape')" class="field">
      <span class="label">Tvar otvoru <HelpBadge @open="$emit('help', 'hole')" /></span>
      <ChoiceChips
        :model-value="values.hole_shape"
        :options="HOLE_SHAPE_OPTIONS"
        @update:model-value="set('hole_shape', $event)"
      />
      <span v-if="errors.hole_shape" class="error">{{ errors.hole_shape }}</span>
    </div>
    <div v-if="shows('hole_size') && measured" class="field">
      <label for="box-hole-size">Šířka otvoru</label>
      <n-input-number
        :input-props="{ id: 'box-hole-size' }"
        :value="values.hole_size"
        :min="1"
        :max="500"
        :show-button="false"
        placeholder="mm"
        class="hole-size"
        @update:value="set('hole_size', $event)"
      >
        <template #suffix>mm</template>
      </n-input-number>
      <span class="hint"
        >Měř nejužší místo. Ozobaný otvor měř tam, kde je nejmenší.</span
      >
      <span v-if="errors.hole_size" class="error">{{ errors.hole_size }}</span>
    </div>
    <div v-if="shows('type')" class="field">
      <label for="box-type">Typ <HelpBadge @open="$emit('help', 'type')" /></label>
      <n-select
        :value="values.type"
        :options="typeOptions"
        :input-props="{ id: 'box-type' }"
        placeholder="Vyber typ"
        clearable
        data-testid="box-type"
        @update:value="set('type', $event)"
      />
      <span v-if="hint" class="tag" :class="hint.tone">{{ hint.text }}</span>
      <span v-if="errors.type" class="error">{{ errors.type }}</span>
    </div>
    <div v-if="shows('opening')" class="field">
      <span class="label"
        >Otevírání <HelpBadge @open="$emit('help', 'opening')"
      /></span>
      <ChoiceChips
        :model-value="values.opening"
        :options="OPENING_OPTIONS"
        @update:model-value="set('opening', $event)"
      />
      <span v-if="errors.opening" class="error">{{ errors.opening }}</span>
    </div>
    <div v-if="shows('material')" class="field">
      <span class="label">Materiál</span>
      <ChoiceChips
        :model-value="values.material"
        :options="MATERIAL_OPTIONS"
        @update:model-value="set('material', $event)"
      />
    </div>
    <div v-if="shows('installed_on')" class="field">
      <label for="box-installed-on">Datum vyvěšení</label>
      <n-date-picker
        :formatted-value="values.installed_on"
        value-format="yyyy-MM-dd"
        format="d. M. yyyy"
        type="date"
        clearable
        :input-props="{ id: 'box-installed-on' }"
        @update:formatted-value="set('installed_on', $event)"
      />
    </div>
  </div>
</template>

<style scoped>
.box-fields {
  display: grid;
  gap: 18px;
}

.hole-size {
  max-width: 160px;
}

.field > .tag {
  justify-self: start;
}
</style>
