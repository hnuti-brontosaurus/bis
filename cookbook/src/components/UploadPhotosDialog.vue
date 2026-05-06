<script setup>
import { computed } from "vue"
import {
  NModal,
  NCard,
  NProgress,
  NList,
  NListItem,
  NThing,
  NIcon,
  NSpin,
  NButton,
  NFlex,
  NText,
} from "naive-ui"
import {
  faCircleCheck,
  faCircleExclamation,
  faClock,
} from "@fortawesome/free-solid-svg-icons"
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome"

const props = defineProps({
  show: { type: Boolean, default: false },
  state: { type: Object, required: true },
})
const emit = defineEmits(["update:show", "retry", "close"])

const closable = computed(
  () => props.state.phase === "partial" || props.state.phase === "done",
)

const title = computed(() => {
  switch (props.state.phase) {
    case "saving-text":
      return "Ukládám recept…"
    case "uploading":
      return "Nahrávám fotky…"
    case "publishing":
      return "Zveřejňuji recept…"
    case "partial":
      return "Některé fotky se nepodařilo nahrát"
    case "done":
      return "Hotovo"
    default:
      return ""
  }
})

const failedCount = computed(
  () => props.state.uploads.filter(u => u.status === "failed").length,
)

const itemLabel = upload => {
  if (upload.kind === "recipe") return "Hlavní fotka receptu"
  const stepName = upload.stepName || `Krok ${upload.index + 1}`
  return `${stepName} — fotka`
}

const errorMessage = upload => {
  const status = upload.error?.response?.status
  if (status === 413) return "Fotka je příliš velká pro server."
  if (upload.error?.code === "ECONNABORTED") {
    return "Nahrávání trvalo moc dlouho — zkus pomalejší internet nebo menší fotku."
  }
  if (!upload.error?.response) {
    return "Spojení s internetem se přerušilo."
  }
  return `Chyba: ${status}`
}

const onClose = () => {
  emit("update:show", false)
  emit("close")
}
</script>

<template>
  <n-modal
    :show="show"
    :mask-closable="closable"
    :close-on-esc="closable"
    @update:show="v => emit('update:show', v)"
  >
    <n-card style="max-width: 560px" :title="title">
      <n-flex vertical size="large">
        <n-progress
          type="line"
          :percentage="state.overallProgress"
          :status="state.phase === 'partial' ? 'warning' : 'default'"
        />

        <n-list bordered v-if="state.uploads.length">
          <n-list-item v-for="(u, i) in state.uploads" :key="i">
            <n-thing>
              <template #header>{{ itemLabel(u) }}</template>
              <template #description>
                <n-text v-if="u.status === 'failed'" type="error">
                  {{ errorMessage(u) }}
                </n-text>
              </template>
              <n-flex align="center" justify="space-between">
                <n-progress
                  type="line"
                  :percentage="u.progress || 0"
                  :status="
                    u.status === 'failed'
                      ? 'error'
                      : u.status === 'done'
                        ? 'success'
                        : 'default'
                  "
                  style="flex: 1; max-width: 320px"
                />
                <n-icon v-if="u.status === 'done'" :size="22" color="#18a058">
                  <font-awesome-icon :icon="faCircleCheck" />
                </n-icon>
                <n-icon v-else-if="u.status === 'failed'" :size="22" color="#d03050">
                  <font-awesome-icon :icon="faCircleExclamation" />
                </n-icon>
                <n-spin v-else-if="u.status === 'uploading'" size="small" />
                <n-icon v-else :size="20" color="#999">
                  <font-awesome-icon :icon="faClock" />
                </n-icon>
              </n-flex>
            </n-thing>
          </n-list-item>
        </n-list>

        <n-flex v-if="state.phase === 'partial'" justify="end" size="small">
          <n-button @click="onClose">Zavřít</n-button>
          <n-button type="primary" @click="emit('retry')">
            Zkusit znovu ({{ failedCount }})
          </n-button>
        </n-flex>
      </n-flex>
    </n-card>
  </n-modal>
</template>
