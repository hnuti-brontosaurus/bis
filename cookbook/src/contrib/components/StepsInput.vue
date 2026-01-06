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
import GenericForm from "@/contrib/components/GenericForm.vue"
import { computed } from "vue"

const { width } = useWindowSize()

const value = defineModel("value")
defineProps(["index"])

const inputs = computed(() => [
  { type: "text", key: "name", span: 2, required: true },
  { type: "text", key: "description", extra: { type: "textarea", rows: 2 }, span: 1.5 },
  { type: "image", key: "photo", span: 0.5 },
])
</script>

<template>
  <GenericForm
    v-model:data="value"
    :inputs="inputs"
    group="RecipeStep"
    :path_prefix="`steps[${index}]`"
  />
  <!--  <n-input-group>-->
  <!--    <n-input-->
  <!--        v-model:value="value.name"-->
  <!--        :placeholder="_.RecipeStep.name"-->
  <!--        type="textarea"-->
  <!--    />-->
  <!--    <n-input-->
  <!--        v-model:value="value.description"-->
  <!--        :placeholder="_.RecipeStep.description"-->
  <!--        type="textarea"-->
  <!--    />-->
  <!--  </n-input-group>-->
</template>
