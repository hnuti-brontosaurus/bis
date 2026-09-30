<script setup>
import { NFlex, NCheckbox, NText, NButton, NInput, NInputNumber } from "naive-ui"
import { computed, ref } from "vue"
import { faChevronRight, faPlus, faTrash } from "@fortawesome/free-solid-svg-icons"
import { useRender } from "@/contrib/composables/render.js"
import { useCartStore } from "@/data/cart.js"
import { _ } from "@/composables/translations.js"

const props = defineProps({
  editable: { type: Boolean, default: false },
  hideBought: { type: Boolean, default: false },
})

const { icon } = useRender()
const cart = useCartStore()

const visibleItems = computed(() =>
  props.hideBought ? cart.otherItems.filter(item => !item.bought) : cart.otherItems,
)

// On the shopping tab the rows line up with ShoppingList's ingredient rows:
// expand chevron, 110px amount, 90px unit.
const countWidth = computed(() => (props.editable ? "90px" : "110px"))

const newName = ref("")
const newCount = ref(1)

const onAdd = () => {
  const name = newName.value.trim()
  if (!name) return
  cart.addOtherItem(name, newCount.value ?? 1)
  newName.value = ""
  newCount.value = 1
}
</script>

<template>
  <n-flex vertical :size="8">
    <div class="section-heading">{{ _.cart.other_items }}</div>

    <n-flex
      v-for="item in visibleItems"
      :key="item.id"
      align="center"
      :wrap="false"
      :size="8"
      :style="{ opacity: !editable && item.bought ? 0.55 : 1 }"
    >
      <n-checkbox v-model:checked="item.bought" />
      <n-button
        v-if="!editable"
        quaternary
        size="small"
        :render-icon="icon(faChevronRight)"
        style="visibility: hidden"
      />
      <n-input v-if="editable" v-model:value="item.name" size="small" style="flex: 1" />
      <n-text
        v-else
        :style="{ flex: 1, textDecoration: item.bought ? 'line-through' : 'none' }"
      >
        {{ item.name }}
      </n-text>
      <n-input-number
        v-model:value="item.count"
        size="small"
        :style="{ width: countWidth }"
        :min="1"
      />
      <n-text v-if="!editable" style="width: 90px; padding-left: 12px">
        {{ _.cart.pieces }}
      </n-text>
      <n-button
        v-else
        quaternary
        circle
        size="small"
        :render-icon="icon(faTrash)"
        @click="cart.removeOtherItem(item.id)"
      />
    </n-flex>

    <n-flex align="center" :wrap="false" :size="8">
      <n-input
        v-model:value="newName"
        size="small"
        :placeholder="_.cart.other_item_placeholder"
        style="flex: 1"
        @keydown.enter="onAdd"
      />
      <n-input-number
        v-model:value="newCount"
        size="small"
        :style="{ width: countWidth }"
        :min="1"
      />
      <n-button
        type="primary"
        size="small"
        :render-icon="icon(faPlus)"
        :disabled="!newName.trim()"
        :style="editable ? undefined : { width: '90px' }"
        @click="onAdd"
      />
    </n-flex>
  </n-flex>
</template>
