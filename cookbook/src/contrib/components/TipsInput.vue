<script setup>
import { computed } from "vue"
import GenericForm from "@/contrib/components/GenericForm.vue"

const value = defineModel("value")
defineProps(["index"])

const inputs = computed(() => [
  { type: "text", key: "name", required: true, max_length: 31 },
  { type: "html", key: "description", required: true },
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
