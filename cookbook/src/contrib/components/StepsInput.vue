<script setup>
import { NCollapseTransition } from "naive-ui"
import GenericForm from "@/contrib/components/GenericForm.vue"

const value = defineModel("value")
defineProps({ index: Number, showDetails: Boolean })

const nameInput = [
  { type: "text", key: "name", span: 2, required: true, hide_label: true },
]
const detailInputs = [
  { type: "text", key: "description", extra: { type: "textarea", rows: 2 }, span: 1 },
  { type: "checkbox", key: "is_optional", span: 0.5, hide_label: true },
  { type: "image", key: "photo", span: 0.5 },
]
</script>

<template>
  <GenericForm
    v-model:data="value"
    :inputs="nameInput"
    group="RecipeStep"
    :path_prefix="`steps[${index}]`"
  />
  <n-collapse-transition :show="showDetails">
    <GenericForm
      v-model:data="value"
      :inputs="detailInputs"
      group="RecipeStep"
      :path_prefix="`steps[${index}]`"
    />
  </n-collapse-transition>
</template>
