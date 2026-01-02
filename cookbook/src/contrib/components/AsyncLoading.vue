<script setup>
import { NResult, NSpin } from "naive-ui"
import { computed, ref } from "vue"

const loading = ref(false)
const error = ref(false)

function load(promise) {
  loading.value = true
  error.value = false
  return promise
    .catch(e => {
      error.value = true
      throw e
    })
    .finally(() => (loading.value = false))
}

const style = computed(() =>
  loading.value ? { minWidth: "5rem", minHeight: "5rem" } : {},
)

defineExpose({ load })
</script>

<template>
  <n-spin :show="loading" :style="style">
    <n-result v-show="error" size="small" status="error"></n-result>
    <div v-show="!error">
      <slot></slot>
    </div>
  </n-spin>
</template>
