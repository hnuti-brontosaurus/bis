<script setup>
import {
  NAlert,
  NButton,
  NCard,
  NFlex,
  NForm,
  NFormItem,
  NInput,
  NModal,
  NSelect,
  NText,
} from "naive-ui"
import { computed, ref, watch } from "vue"
import axios from "axios"
import { useRecipeTagsStore } from "@/data/recipeTags.js"
import { handleAxiosError } from "@/contrib/composables/setup.js"
import { _ } from "@/composables/translations.js"

const props = defineProps({ groups: { type: Array, required: true } })
const show = defineModel("show", { type: Boolean, default: false })
const emit = defineEmits(["created"])

const tagsStore = useRecipeTagsStore()
const group = ref(null)
const name = ref("")
const errors = ref({})
const saving = ref(false)

watch(show, value => {
  if (!value) return
  group.value = null
  name.value = ""
  errors.value = {}
})

const groupOptions = computed(() =>
  props.groups.map(value => ({ label: value, value })),
)
const canSave = computed(() => group.value && name.value.trim())

const save = async () => {
  saving.value = true
  errors.value = {}
  try {
    const tag = await tagsStore.save({ group: group.value, name: name.value.trim() })
    emit("created", tag)
    show.value = false
  } catch (e) {
    if (axios.isAxiosError(e) && e.response?.status === 400)
      errors.value = e.response.data
    else handleAxiosError(_.value.edit_recipe.add_tag_error)(e)
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <n-modal v-model:show="show">
    <n-card
      :title="_.edit_recipe.add_tag"
      :bordered="false"
      closable
      role="dialog"
      style="max-width: 480px; width: 90vw"
      @close="show = false"
    >
      <n-form @submit.prevent="save">
        <n-form-item
          :label="_.edit_recipe.tag_group"
          :validation-status="errors.group ? 'error' : undefined"
          :feedback="errors.group?.join(' ')"
        >
          <n-select v-model:value="group" :options="groupOptions" filterable />
        </n-form-item>
        <n-form-item
          :label="_.edit_recipe.tag_name"
          :validation-status="errors.name ? 'error' : undefined"
          :feedback="errors.name?.join(' ')"
        >
          <n-input v-model:value="name" :maxlength="31" show-count placeholder="" />
        </n-form-item>
      </n-form>
      <n-flex vertical>
        <n-alert type="warning" :show-icon="false">
          {{ _.edit_recipe.add_tag_warning }}
        </n-alert>
        <n-text depth="3">{{ _.edit_recipe.add_tag_note }}</n-text>
      </n-flex>
      <template #action>
        <n-flex justify="end">
          <n-button @click="show = false">{{ _.common.back }}</n-button>
          <n-button type="primary" :disabled="!canSave" :loading="saving" @click="save">
            {{ _.edit_recipe.add_tag }}
          </n-button>
        </n-flex>
      </template>
    </n-card>
  </n-modal>
</template>
