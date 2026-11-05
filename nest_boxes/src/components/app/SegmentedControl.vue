<script setup>
defineProps({
  options: { type: Array, required: true },
  size: { type: String, default: "" },
  // without the track, for a switch inside a toolbar
  plain: { type: Boolean, default: false },
})

const model = defineModel({ type: [String, Number, Boolean], default: null })
</script>

<template>
  <div class="segmented" :class="[size, { plain }]" role="radiogroup">
    <button
      v-for="option in options"
      :key="String(option.value)"
      type="button"
      role="radio"
      :aria-checked="model === option.value"
      :class="{ on: model === option.value }"
      @click="model = option.value"
    >
      {{ option.label }}
    </button>
  </div>
</template>

<style scoped>
.segmented {
  display: flex;
  padding: 4px;
  gap: 4px;
  background: var(--surface-2);
  border: 1px solid var(--line);
  border-radius: calc(var(--r-btn) + 4px);
}

.segmented button {
  flex: 1;
  min-width: 0;
  padding: 9px 10px;
  border: 1px solid transparent;
  border-radius: var(--r-btn);
  background: transparent;
  color: var(--muted);
  font: 600 15px var(--font);
  cursor: pointer;
}

.segmented button.on {
  background: var(--surface);
  border-color: var(--line-strong);
  color: var(--primary-text);
  font-weight: 800;
  box-shadow: 0 1px 2px var(--shadow-c);
}

.segmented.plain {
  padding: 0;
  gap: 2px;
  background: none;
  border: 0;
}

.segmented.plain button {
  padding: 5px 10px;
  font-size: 14px;
}

.segmented.plain button.on {
  background: var(--primary-soft);
  border-color: transparent;
  box-shadow: none;
}

.segmented.small button {
  padding: 5px 8px;
  font-size: 13.5px;
}
</style>
