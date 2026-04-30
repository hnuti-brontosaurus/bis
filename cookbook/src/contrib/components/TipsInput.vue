<script setup>
import { computed } from "vue"
import GenericForm from "@/contrib/components/GenericForm.vue"

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
