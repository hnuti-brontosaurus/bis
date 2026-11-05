<script setup>
import { computed, ref } from "vue"
import { useMediaQuery } from "@vueuse/core"
import {
  NButton,
  NDatePicker,
  NDrawer,
  NDrawerContent,
  NInput,
  NSwitch,
  useMessage,
} from "naive-ui"

import AppIcon from "@/components/app/AppIcon.vue"
import ChoiceChips from "@/components/app/ChoiceChips.vue"
import HelpBadge from "@/components/app/HelpBadge.vue"
import SegmentedControl from "@/components/app/SegmentedControl.vue"
import BoxFields from "@/components/box/BoxFields.vue"
import HelpPanel from "@/components/check/HelpPanel.vue"
import PhotoPicker from "@/components/check/PhotoPicker.vue"
import {
  asksContents,
  buildPayload,
  chooseReason,
  initialState,
  validate,
} from "@/components/check/checkForm.js"
import { holeLabel, mapyLink } from "@/composables/boxes.js"
import { formatDate } from "@/composables/czech.js"
import { BOX_LEFT_OPTIONS, categoryOptions } from "@/composables/labels.js"
import { reportError } from "@/data/errors.js"

// The interface is documented in old_budky/docs/implementation.md, "Frontend
// components": the volunteer pages pass a submit that saves offline.
const props = defineProps({
  // a manager box or a link box
  box: { type: Object, required: true },
  // a check in the API's shape to edit, or null for a new one
  initial: { type: Object, default: null },
  // categories/: { types, occupants, not_cleaned_reasons, … }
  categories: { type: Object, required: true },
  // help_articles/: [{ slug, title, content }]
  helpArticles: { type: Array, default: () => [] },
  // async (check, { added: [data URI], removed: [photo id] }) => void;
  // a rejection keeps the form open and is reported
  submit: { type: Function, required: true },
  editableDate: { type: Boolean, default: false },
  // ISO date of a new check, when not today: paper forms are entered later
  defaultDate: { type: String, default: undefined },
  // Inside a table row or a list: no pinned save bar, help in a drawer
  inline: { type: Boolean, default: false },
  saveLabel: { type: String, default: "Uložit kontrolu" },
  saveHint: { type: String, default: "" },
  // Help links lead to the help pages, which aren't available offline
  helpLinked: { type: Boolean, default: true },
})

const emit = defineEmits(["cancel"])

const message = useMessage()
const isPhone = useMediaQuery("(max-width: 720px)")

const state = ref(
  initialState(props.box, props.initial, props.categories.types, props.defaultDate),
)
const addedPhotos = ref([])
const removedPhotos = ref([])
const attempted = ref(false)
const saving = ref(false)

const hanging = computed(() => state.value.hanging)
const found = computed(() => state.value.found === "found")
const errors = computed(() =>
  attempted.value ? validate(state.value, props.categories, props.initial) : {},
)

const FOUND_OPTIONS = [
  { value: "not_found", label: "Nenalezena" },
  { value: "not_reached", label: "Nedostali jsme se k ní" },
]
const CLEANING_OPTIONS = [
  { value: "cleaned", label: "Ano" },
  { value: "not_cleaned", label: "Ne" },
]
const CONTENTS_OPTIONS = [
  { value: "nothing", label: "Prázdná" },
  { value: "bird_nest", label: "Hnízdo nebo zbytky po ptácích" },
  { value: "other_animal", label: "Jiné zvíře" },
  { value: "unknown", label: "Nevím" },
]
const WHY_NOT = {
  not_found: {
    label: "Proč se nenašla?",
    placeholder: "Třeba: hledali jsme kolem souřadnic, strom je pokácený",
  },
  not_reached: {
    label: "Proč jste se k ní nedostali?",
    placeholder: "Třeba: oplocený pozemek, rozvodněný potok",
  },
}
const NOT_HUNG = {
  label: "Proč se nepověsila?",
  placeholder: "Třeba: nebyl tam vhodný strom",
}
const BREEDING_OPTIONS = [
  { value: "eggs_left", label: "V hnízdě zůstala vejce" },
  { value: "dead_birds", label: "Mrtvá mláďata nebo ptáci" },
]

const occupantOptions = computed(() =>
  categoryOptions(
    props.categories.occupants.filter(
      occupant => occupant.is_bird === (state.value.contents === "bird_nest"),
    ),
  ),
)
const reasonOptions = computed(() =>
  categoryOptions(props.categories.not_cleaned_reasons),
)
const whyNot = computed(() => (hanging.value ? NOT_HUNG : WHY_NOT[state.value.found]))
const noteId = `check-note-${state.value.id}`

const isFound = computed({
  get: () => (hanging.value ? state.value.hung : found.value),
  set: value => {
    if (hanging.value) state.value.hung = value
    state.value.found = value ? "found" : hanging.value ? "not_reached" : "not_found"
  },
})

const helpTopic = ref(hanging.value ? "hanging" : "contents")
const helpOpen = ref(false)
const helpArticle = computed(
  () =>
    props.helpArticles.find(article => article.slug === helpTopic.value) ?? {
      slug: helpTopic.value,
      title: "",
      content: "",
    },
)
const sideHelp = computed(() => !props.inline && !isPhone.value)

const openHelp = slug => {
  helpTopic.value = slug
  if (!sideHelp.value) helpOpen.value = true
}

const save = async () => {
  attempted.value = true
  if (Object.keys(errors.value).length) {
    message.warning("Ještě něco chybí, je to vyznačené červeně.")
    return
  }
  saving.value = true
  try {
    await props.submit(buildPayload(state.value, props.box, props.categories), {
      added: addedPhotos.value,
      removed: removedPhotos.value,
    })
  } catch (error) {
    reportError(error)
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="check-form" :class="{ inline }" data-testid="check-form">
    <div class="layout">
      <div class="questions">
        <div class="row">
          <n-date-picker
            v-if="editableDate"
            v-model:formatted-value="state.date"
            value-format="yyyy-MM-dd"
            format="d. M. yyyy"
            type="date"
            size="small"
            class="date"
            :input-props="{ 'aria-label': 'Datum kontroly' }"
          />
          <span v-else class="tag"
            ><AppIcon name="clock" />{{ formatDate(state.date) }}</span
          >
          <span v-if="holeLabel(box)" class="tag">otvor {{ holeLabel(box) }}</span>
          <span v-if="box.installed_on" class="tag">
            vyvěšena {{ box.installed_on.slice(0, 4) }}
          </span>
          <span v-if="!box.is_verified && !hanging" class="tag warn">neověřená</span>
          <span class="spacer" />
          <a class="mapy small" :href="mapyLink(box.location)" target="_blank">
            <AppIcon name="ext" />Mapy.com
          </a>
        </div>
        <span v-if="errors.date" class="error">{{ errors.date }}</span>

        <div class="form-card">
          <div class="question">
            <div class="row">
              <span class="label grow">
                {{ hanging ? "Budka pověšena" : "Budka nalezena" }}
                <HelpBadge @open="openHelp(hanging ? 'hanging' : 'found')" />
              </span>
              <n-switch
                v-model:value="isFound"
                :aria-label="hanging ? 'Budka pověšena' : 'Budka nalezena'"
              />
            </div>
            <SegmentedControl
              v-if="!isFound && !hanging"
              v-model="state.found"
              :options="FOUND_OPTIONS"
            />
            <div v-if="!found" class="reveal">
              <label class="label" :for="noteId">{{ whyNot.label }}</label>
              <n-input
                v-model:value="state.note"
                type="textarea"
                :autosize="{ minRows: 2 }"
                :input-props="{ id: noteId }"
                :placeholder="whyNot.placeholder"
              />
              <span v-if="errors.note" class="error">{{ errors.note }}</span>
            </div>
          </div>

          <template v-if="found && !hanging">
            <div class="question">
              <span class="label">
                Vyčištěno <HelpBadge @open="openHelp('cleaning')" />
              </span>
              <SegmentedControl v-model="state.cleaning" :options="CLEANING_OPTIONS" />
              <div v-if="state.cleaning === 'not_cleaned'" class="reveal">
                <span class="label">Proč ne?</span>
                <ChoiceChips
                  :model-value="state.not_cleaned_reason_id"
                  :options="reasonOptions"
                  @update:model-value="chooseReason(state, $event, categories)"
                />
                <span v-if="errors.not_cleaned_reason_id" class="error">
                  {{ errors.not_cleaned_reason_id }}
                </span>
              </div>
            </div>

            <div v-if="asksContents(state, categories)" class="question">
              <span class="label">
                Co v budce bylo? <HelpBadge @open="openHelp('contents')" />
              </span>
              <span class="small muted">
                Hnízdo nebo zbytky po zvířatech se počítají, i když už tam nikdo není.
              </span>
              <ChoiceChips v-model="state.contents" :options="CONTENTS_OPTIONS" />
              <span v-if="errors.contents" class="error">{{ errors.contents }}</span>
              <div
                v-if="['bird_nest', 'other_animal'].includes(state.contents)"
                class="reveal"
              >
                <span class="label">
                  {{
                    state.contents === "bird_nest" ? "Kdo tu hnízdil?" : "Jaké zvíře?"
                  }}
                  <span class="small muted light">
                    Můžeš vybrat víc. „Nevím“ je lepší než tip.
                  </span>
                </span>
                <ChoiceChips
                  v-model="state.occupant_ids"
                  :options="occupantOptions"
                  multiple
                />
                <span v-if="errors.occupant_ids" class="error">
                  {{ errors.occupant_ids }}
                </span>
                <button
                  class="text-button small"
                  type="button"
                  @click="openHelp('occupants')"
                >
                  <AppIcon name="help" /> Jak poznat, kdo tu bydlel
                </button>
                <template v-if="state.contents === 'bird_nest'">
                  <ChoiceChips
                    v-model="state.breeding"
                    :options="BREEDING_OPTIONS"
                    multiple
                  />
                  <n-input
                    v-model:value="state.breeding_note"
                    placeholder="Poznámka k hnízdění, třeba kolik vajec"
                  />
                </template>
              </div>
            </div>

            <div class="question">
              <span class="label">
                Stav budky <HelpBadge @open="openHelp('box_left')" />
              </span>
              <ChoiceChips v-model="state.box_left" :options="BOX_LEFT_OPTIONS" />
            </div>
          </template>

          <div v-if="found" class="question">
            <template v-if="state.verify">
              <span class="label">
                Prosím ověř údaje budky
                <HelpBadge @open="openHelp(hanging ? 'hanging' : 'box_changes')" />
              </span>
              <span class="small muted">
                {{
                  hanging
                    ? "Zadej, kde budka visí, a zkontroluj otvor, typ a otevírání."
                    : "Údaje budky nejsou ověřené nebo úplné. Zkontroluj je a doplň, co chybí."
                }}
              </span>
            </template>
            <button
              v-else
              class="collapse"
              type="button"
              :aria-expanded="state.changes_open"
              @click="state.changes_open = !state.changes_open"
            >
              <AppIcon name="edit" />
              <span class="grow">
                <b>Něco se na budce změnilo</b>
                <span class="small muted">Otvor, typ, otevírání, poloha, označení</span>
              </span>
              <AppIcon :name="state.changes_open ? 'minus' : 'chevd'" />
            </button>
            <div v-if="state.changes_open" class="reveal">
              <BoxFields
                v-model="state.changes"
                :types="categories.types"
                :center="box.location"
                :errors="errors"
                :locate-on-open="hanging && !initial"
                @help="openHelp"
              />
            </div>
          </div>

          <div class="question">
            <span class="label">
              Fotky
              <span class="small muted light">nepovinné, pro nejasné případy</span>
            </span>
            <PhotoPicker
              v-model:added="addedPhotos"
              v-model:removed="removedPhotos"
              :existing="initial?.photos ?? []"
            />
          </div>

          <div v-if="found" class="question">
            <label class="label" :for="noteId">Poznámka</label>
            <n-input
              v-model:value="state.note"
              type="textarea"
              :autosize="{ minRows: 2 }"
              :input-props="{ id: noteId }"
              placeholder="Cokoli dalšího, co by měl správce vědět"
            />
          </div>
        </div>
      </div>
      <aside v-if="sideHelp" class="side-help card">
        <HelpPanel :article="helpArticle" :linked="helpLinked" @help="openHelp" />
      </aside>
    </div>

    <div class="save-bar">
      <n-button type="primary" size="large" :loading="saving" @click="save">
        <template #icon><AppIcon name="check" /></template>
        {{ saveLabel }}
      </n-button>
      <n-button v-if="inline" size="large" @click="emit('cancel')">Zrušit</n-button>
      <span v-if="saveHint" class="small muted hint">{{ saveHint }}</span>
      <span class="spacer" />
      <slot name="actions" />
    </div>

    <n-drawer
      v-model:show="helpOpen"
      :placement="isPhone ? 'bottom' : 'right'"
      :height="'70%'"
      :width="420"
    >
      <n-drawer-content closable>
        <HelpPanel :article="helpArticle" :linked="helpLinked" @help="openHelp" />
      </n-drawer-content>
    </n-drawer>
  </div>
</template>

<style scoped>
.check-form {
  display: grid;
  gap: 0;
}

.layout {
  display: grid;
  grid-template-columns: minmax(0, 1.6fr) minmax(0, 1fr);
  gap: 24px;
  align-items: start;
}

.inline .layout {
  grid-template-columns: minmax(0, 1fr);
}

.questions {
  display: grid;
  gap: 12px;
  min-width: 0;
}

.form-card {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--r);
  box-shadow: var(--card-shadow);
}

.question {
  display: grid;
  gap: 10px;
  padding: 18px 20px;
}

.question + .question {
  border-top: 1px solid var(--line);
}

.label {
  font-weight: 700;
  font-size: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.light {
  font-weight: 400;
}

.grow {
  flex: 1;
}

.reveal {
  display: grid;
  gap: 10px;
  padding: 14px;
  border-radius: var(--r-in);
  background: var(--surface-2);
}

.group-label {
  font: 700 12px var(--font);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--muted);
}

.error {
  font-size: 13px;
  font-weight: 700;
  color: var(--danger);
}

.collapse {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  padding: 0;
  border: 0;
  background: none;
  color: inherit;
  font: inherit;
  text-align: left;
  cursor: pointer;
}

.collapse .grow {
  display: grid;
  gap: 2px;
}

.collapse > .icon:first-child {
  color: var(--primary-text);
}

.text-button {
  justify-self: start;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 0;
  border: 0;
  background: none;
  color: var(--primary-text);
  font: 700 13px var(--font);
  cursor: pointer;
}

.text-button .icon {
  width: 16px;
  height: 16px;
}

.mapy {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-weight: 700;
  text-decoration: none;
}

.mapy .icon {
  width: 16px;
  height: 16px;
}

.date {
  width: 150px;
}

.side-help {
  position: sticky;
  top: 16px;
  max-height: calc(100dvh - 120px);
  overflow: auto;
}

.save-bar {
  position: sticky;
  bottom: 0;
  z-index: 2;
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  margin-top: 16px;
  padding: 14px 0;
  background: var(--bg);
  border-top: 1px solid var(--line);
}

.inline .save-bar {
  position: static;
  background: none;
  border-top: 0;
  padding: 0;
}

.save-bar .hint {
  flex: 1;
  min-width: 180px;
}

@media (max-width: 720px) {
  .layout {
    grid-template-columns: minmax(0, 1fr);
  }

  .question {
    padding: 16px;
  }

  .save-bar {
    margin: 16px -16px 0;
    padding: 12px 16px;
  }

  .inline .save-bar {
    margin: 16px 0 0;
    padding: 0;
  }
}
</style>
