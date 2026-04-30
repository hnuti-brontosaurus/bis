<script setup>
import GenericForm from "@/contrib/components/GenericForm.vue"
import { computed } from "vue"

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
