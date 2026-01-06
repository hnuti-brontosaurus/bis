<script setup>
import {
  NButton,
  NCascader,
  NCheckbox,
  NDivider,
  NDatePicker,
  NUpload,
  NFlex,
  NFormItemGi,
  NGrid,
  NInput,
  NInputGroup,
  NInputNumber,
  NDynamicTags,
  NCollapse,
  NCollapseItem,
  NSelect,
  NDynamicInput,
  NH6,
  NButtonGroup,
} from "naive-ui"
import { computed, isRef, onMounted, ref, toValue, watch } from "vue"

import { textFilter, toValueLabel } from "@/contrib/composables/helpers.js"
import WithHint from "@/contrib/components/WithHint.vue"
import { _ } from "@/composables/translations.js"
import IngredientInput from "@/contrib/components/IngredientInput.vue"
import { icon } from "@/contrib/composables/render.js"
import {
  faArrowDown,
  faArrowUp,
  faMinus,
  faPlus,
} from "@fortawesome/free-solid-svg-icons"
import StepsInput from "@/contrib/components/StepsInput.vue"
import TipsInput from "@/contrib/components/TipsInput.vue"

const props = defineProps(["inputs", "path_prefix", "group"])
const data = defineModel("data")
const getRule = input => {
  const rules = []
  if (input.required) {
    const config = {
      required: true,
      trigger: "input",
      message: _.value.common.required,
      key: input.key,
    }
    if (typeof input.required === "string") config.type = input.required
    if (input.type === "number") config.type = "number"
    if ((input.type === "select" && input.extra?.multiple) || input.type === "tags") {
      config.type = "object"
      config.validator = (rule, value) => !!value.length
    }
    if (input.type === "image") config.type = "object"
    rules.push(config)
  }
  if (input.type === "image")
    rules.push({
      trigger: "change",
      validator: async (rule, value) =>
        new Promise((resolve, reject) => {
          const reader = new FileReader()

          reader.onload = () => {
            const result = reader.result
            const [prefix, base64Data] = result.split(",")

            value.base64data = `data:${value.type};filename=${value.name};base64,${base64Data}`
            resolve()
          }
          reader.onerror = error => reject(error)

          if (value?.file) reader.readAsDataURL(value.file)
          else resolve()
        }),
    })
  if (input.rules) rules.push(...input.rules)
  return rules
}

const cascaderFilter = (pattern, option, path) => {
  return textFilter(pattern, [path], item => item.map(i => i.label)).length
}

const setDefault = input => {
  if (input.type === "checkboxes")
    input.checkboxes.forEach(item => {
      setDefaultValue(item, item.default === undefined ? false : !!item.default)
    })
  else setDefaultValue(input, input.default)

  if (
    input.type === "select" &&
    Array.isArray(toValue(input.options)) &&
    input.required
  )
    setDefaultValue(input, toValueLabel(input.options)[0]?.value)
}

const watchRefOptions = input => {
  watch(
    input.options,
    options => setDefaultValue(input, toValue(toValueLabel(options)[0]?.value)),
    { immediate: true },
  )
}
onMounted(() => {
  props.inputs.forEach(setDefault)
  props.inputs
    .filter(input => input.type === "select" && isRef(input.options) && input.required)
    .forEach(watchRefOptions)
})

const getValue = input => (input.value ? input.value.value : data.value[input.key])
const setValue = (input, value) => {
  if (!input.key) return
  if (input.value) input.value.value = value
  else data.value[input.key] = value
}
const valueExists = input => {
  const value = getValue(input)
  if (Array.isArray(value)) return true
  if (typeof value === "number") return true
  if (value === false) return true
  return value
}
const setDefaultValue = (input, value) => {
  value ??= undefined
  if (!valueExists(input)) setValue(input, value)
}

const computedValue = input =>
  computed({
    get: () => getValue(input),
    set: value => setValue(input, value),
  })

const shownInputs = computed(() =>
  props.inputs
    .filter(input => !input.only_if || input.only_if(data.value))
    .map(input => ({
      ...input,
      label:
        input.key && !input.hide_label ? _.value[props.group][input.key] : undefined,
      value: computedValue(input),
      shown_options: toValue(input.options),
      checkboxes: input.checkboxes?.map(checkbox => ({
        ...checkbox,
        value: computedValue(checkbox),
      })),
    }))
    .map(input =>
      input.type !== "image"
        ? input
        : {
            ...input,
            file_list: computed({
              get: () =>
                input.value.value
                  ? [
                      {
                        ...input.value.value,
                        id: "1",
                        url: input.value.value.small,
                        status: "finished",
                      },
                    ]
                  : [],
              set: value => (input.value.value = value[0]),
            }),
          },
    ),
)

const prefix = computed(() => (props.path_prefix ? `${props.path_prefix}.` : ""))
const getStyle = input => (input.new_line ? { gridColumnStart: 1 } : {})
</script>

<template>
  <n-grid cols="2 s:4" x-gap="32" responsive="screen">
    <n-form-item-gi
      v-for="input in shownInputs"
      :key="input.key"
      :path="`${prefix}${input.key}`"
      :rule="getRule(input)"
      :show-feedback="!input.hide_feedback"
      :show-label="!!input.label"
      :span="(input.span ?? 1) * 2"
      :style="getStyle(input)"
      v-bind="input.item"
      require-mark-placement="left"
    >
      <template #label>
        <WithHint :hint="toValue(input.hint)">{{ input.label }}</WithHint>
      </template>
      <n-input-group
        style="justify-content: end; align-items: end; flex-direction: column"
      >
        <n-h6 v-if="input.title && input.type !== 'section'" style="width: 100%">
          {{ input.title }}
        </n-h6>
        <n-input
          v-if="input.type === 'text'"
          v-model:value="input.value.value"
          :clearable="!input.required"
          placeholder=""
          v-bind="input.extra"
        />

        <n-input-number
          v-if="input.type === 'number'"
          v-model:value="input.value.value"
          :clearable="!input.required"
          placeholder=""
          v-bind="input.extra"
        />

        <n-select
          v-if="input.type === 'select'"
          v-model:value="input.value.value"
          :clearable="!input.required"
          :options="toValueLabel(input.shown_options)"
          placeholder=""
          filterable
          show-on-focus
          v-bind="input.extra"
        />

        <n-cascader
          v-if="input.type === 'cascader'"
          v-model:value="input.value.value"
          :clearable="!input.required"
          :filter="cascaderFilter"
          :options="toValue(input.shown_options)"
          placeholder=""
          check-strategy="child"
          expand-trigger="hover"
          filterable
          show-path
          v-bind="input.extra"
        />

        <n-date-picker
          v-if="['date', 'datetime'].includes(input.type)"
          v-model:formatted-value="input.value.value"
          :clearable="!input.required"
          placeholder=""
          :type="input.type"
          v-bind="input.extra"
        />

        <n-dynamic-tags
          v-if="input.type === 'tags'"
          v-model:value="input.value.value"
          v-bind="input.extra"
        />

        <n-upload
          v-if="input.type === 'image'"
          list-type="image-card"
          v-model:file-list="input.file_list.value"
          v-bind="input.extra"
          :max="1"
          :show-preview-button="false"
          >Přidat
        </n-upload>

        <n-collapse v-if="input.type === 'section'">
          <n-collapse-item>
            <template #header>
              <n-h6 v-if="input.title" :style="{ margin: '6px 0' }">{{
                input.title
              }}</n-h6>
            </template>
            <n-dynamic-input
              v-model:value="input.value.value"
              show-sort-button
              v-bind="input.extra"
              :on-create="() => ({})"
              item-style="align-items: center; flex-direction: column-reverse;"
              :create-button-props="{ size: 'small', 'render-icon': icon(faPlus) }"
            >
              <template #create-button-default>&nbsp;</template>
              <template #default="{ value, index }">
                <n-flex vertical style="width: 100%">
                  <IngredientInput
                    :index="index"
                    :value="value"
                    v-if="input.key === 'ingredients'"
                  />
                  <StepsInput
                    :index="index"
                    :value="value"
                    v-if="input.key === 'steps'"
                  />
                  <TipsInput
                    :index="index"
                    :value="value"
                    v-if="input.key === 'tips'"
                  />
                  <n-button
                    @click="() => input.value.value.push({})"
                    v-if="index + 1 === input.value.value.length"
                    ghost
                    dashed
                    :render-icon="icon(faPlus)"
                    size="small"
                  ></n-button>
                </n-flex>
              </template>
              <template #action="{ index, create, remove, move }">
                <n-flex style="width: 100%" :wrap="false">
                  <n-divider title-placement="left"
                    >{{ index + 1 }}. {{ _.section[input.key] }}</n-divider
                  >
                  <n-button-group style="margin-left: 1rem; align-items: center">
                    <n-button
                      @click="() => remove(index)"
                      :render-icon="icon(faMinus)"
                      size="tiny"
                    />
                    <n-button
                      @click="() => move('up', index)"
                      :render-icon="icon(faArrowUp)"
                      size="tiny"
                    />
                    <n-button
                      @click="() => move('down', index)"
                      :render-icon="icon(faArrowDown)"
                      size="tiny"
                    />
                    <n-button
                      @click="() => create(index)"
                      :render-icon="icon(faPlus)"
                      size="tiny"
                    />
                  </n-button-group>
                </n-flex>
              </template>
            </n-dynamic-input>
          </n-collapse-item>
        </n-collapse>

        <n-dynamic-input
          v-if="input.type === 'dynamic-input-select'"
          v-model:value="input.value.value"
          placeholder=""
          show-sort-button
          v-bind="input.extra"
          :on-create="() => ({ key: toValueLabel(input.shown_options)[0].key })"
        >
          <template #create-button-default>Add</template>
          <template #default="{ value }">
            <n-select
              v-model:value="value.key"
              :options="toValueLabel(input.shown_options)"
              filterable
              :clearable="false"
              placeholder=""
              show-on-focus
              @update:value="input.value.value = input.value.value"
            ></n-select>
          </template>
        </n-dynamic-input>

        <n-flex
          v-if="input.type === 'checkboxes'"
          :vertical="input.vertical"
          style="width: 100%"
        >
          <component
            v-for="item in input.checkboxes"
            :is="NCheckbox"
            :key="item.key"
            v-model:checked="item.value.value"
          >
            <WithHint :hint="toValue(item.hint)">{{ toValue(item.label) }}</WithHint>
          </component>
        </n-flex>

        <n-button-group v-if="input.action">
          <n-button
            v-if="input.action"
            @click="input.action.onClick"
            v-bind="input.action.extra"
            >{{ toValue(input.action.label) }}
          </n-button>
        </n-button-group>
      </n-input-group>
    </n-form-item-gi>
  </n-grid>
</template>
