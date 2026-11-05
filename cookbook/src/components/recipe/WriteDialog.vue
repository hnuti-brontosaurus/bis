<script setup>
import { NButton, NCard, NFlex, NForm, NModal } from "naive-ui"
import { computed, ref, watch } from "vue"
import GenericForm from "@/contrib/components/GenericForm.vue"
import { handleAxiosError } from "@/contrib/composables/setup.js"
import { _ } from "@/composables/translations.js"

// A text with photos written in a modal: a recipe comment or note.
const props = defineProps({
  title: { type: String, required: true },
  group: { type: String, required: true },
  textKey: { type: String, required: true },
  textRequired: Boolean,
  initial: { type: Object, required: true },
  save: { type: Function, required: true },
})
const show = defineModel("show", { type: Boolean, default: false })

const form = ref()
const value = ref()
const saving = ref(false)

watch(show, shown => {
  if (shown) value.value = JSON.parse(JSON.stringify(props.initial))
})

const inputs = computed(() => [
  {
    type: "html",
    key: props.textKey,
    hide_label: true,
    required: props.textRequired,
    span: 2,
  },
  { type: "images", key: "photos", span: 2 },
])

const onSave = async () => {
  await form.value.validate()
  saving.value = true
  try {
    await props.save(value.value)
    show.value = false
  } catch (e) {
    handleAxiosError(_.value.common.save_error)(e)
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <n-modal v-model:show="show" :mask-closable="false">
    <n-card
      :title="title"
      :bordered="false"
      closable
      role="dialog"
      style="max-width: 640px; width: 90vw"
      @close="show = false"
    >
      <n-form ref="form" :model="value">
        <GenericForm v-model:data="value" :inputs="inputs" :group="group" />
      </n-form>
      <slot :value="value" />
      <template #action>
        <n-flex justify="end">
          <n-button @click="show = false">{{ _.common.back }}</n-button>
          <n-button type="primary" :loading="saving" @click="onSave">
            {{ _.common.save }}
          </n-button>
        </n-flex>
      </template>
    </n-card>
  </n-modal>
</template>
