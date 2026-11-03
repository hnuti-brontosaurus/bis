<script setup>
import AppIcon from "@/components/app/AppIcon.vue"

const props = defineProps({
  options: { type: Array, required: true },
  multiple: { type: Boolean, default: false },
})

const model = defineModel({ type: [String, Array], default: null })

const isOn = value =>
  props.multiple ? model.value.includes(value) : model.value === value

const toggle = value => {
  if (!props.multiple) model.value = value
  else if (isOn(value)) model.value = model.value.filter(item => item !== value)
  else model.value = [...model.value, value]
}
</script>

<template>
  <div class="chips" :role="multiple ? 'group' : 'radiogroup'">
    <button
      v-for="option in options"
      :key="option.value"
      type="button"
      class="chip"
      :class="{ on: isOn(option.value) }"
      :role="multiple ? 'checkbox' : 'radio'"
      :aria-checked="isOn(option.value)"
      @click="toggle(option.value)"
    >
      <AppIcon v-if="isOn(option.value)" name="check" />
      {{ option.label }}
    </button>
  </div>
</template>

<style scoped>
.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 7px 14px;
  border-radius: var(--r-chip);
  border: 1px solid var(--line-strong);
  background: var(--surface);
  color: var(--text);
  font: 400 14.5px var(--font);
  white-space: nowrap;
  cursor: pointer;
}

.chip .icon {
  width: 16px;
  height: 16px;
}

.chip.on {
  background: var(--primary-soft);
  border-color: var(--primary);
  color: var(--primary-text);
  font-weight: 700;
}
</style>
