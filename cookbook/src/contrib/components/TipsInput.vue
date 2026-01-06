<script setup>
import { NInputGroup, NSelect, NText, NInputNumber, NInput } from "naive-ui"
import { useWindowSize } from "@vueuse/core"
import { propertyRef, toValueLabel } from "@/contrib/composables/helpers.js"
import {
  chefs,
  dataIdMapping,
  dataOptions,
  ingredients,
  units,
} from "@/composables/connector.js"
import { _ } from "@/composables/translations.js"
import { computed } from "vue"
import GenericForm from "@/contrib/components/GenericForm.vue"

const { width } = useWindowSize()

const value = defineModel("value")
defineProps(["index"])

const inputs = computed(() => [
  { type: "text", key: "name", required: true },
  {
    type: "text",
    key: "description",
    extra: { type: "textarea", rows: 2 },
    required: true,
  },
])
</script>

<template>
  <GenericForm
    v-model:data="value"
    :inputs="inputs"
    group="RecipeTip"
    :path_prefix="`tips[${index}]`"
  />
</template>
