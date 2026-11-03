<script setup>
import { reactive, ref } from "vue"
import { NButton, NForm, NFormItem, NInput } from "naive-ui"

import AppIcon from "@/components/app/AppIcon.vue"
import ChoiceChips from "@/components/app/ChoiceChips.vue"
import { reportError } from "@/data/errors.js"
import { sendWantToHang } from "@/data/public.js"

const BOX_COUNTS = [
  { value: "1-5", label: "1–5" },
  { value: "6-20", label: "6–20" },
  { value: "more", label: "víc než 20" },
  { value: "unknown", label: "nevím" },
]

const BOX_SOURCES = [
  { value: "have", label: "Už je máme" },
  { value: "make", label: "Chceme je vyrobit" },
  { value: "advice", label: "Potřebujeme poradit" },
]

const STEPS = [
  ["Ozveme se do týdne", "a zeptáme se na místo."],
  ["Vybereme místo", "a typy budek podle toho, kdo tam žije."],
  ["Vyrobíte nebo dostanete budky", "a pověsíte je, ideálně do února."],
  ["Každý podzim je vyčistíte", "s odkazem do telefonu bez registrace."],
]

const required = message => ({ required: true, message, trigger: "blur" })

const rules = {
  name: required("Napiš, jak ti máme říkat."),
  email: [
    required("Bez e-mailu se ti neozveme."),
    { type: "email", message: "Tohle nevypadá jako e-mail.", trigger: "blur" },
  ],
  place: required("Napiš aspoň obec."),
}

const form = ref(null)
const values = reactive({
  name: "",
  email: "",
  phone: "",
  place: "",
  box_count: null,
  box_source: null,
  message: "",
})
const serverErrors = ref({})
const sending = ref(false)
const sent = ref(false)

// naive-ui rejects on an invalid form; the form already shows why.
const isValid = () =>
  form.value.validate().then(
    () => true,
    () => false,
  )

const submit = async () => {
  if (!(await isValid())) return
  sending.value = true
  serverErrors.value = {}
  try {
    await sendWantToHang(values)
    sent.value = true
  } catch (error) {
    if (error.response?.status === 400) serverErrors.value = error.response.data
    else reportError(error)
  } finally {
    sending.value = false
  }
}

const feedback = field => serverErrors.value[field]?.join(" ")
</script>

<template>
  <main class="page">
    <div class="two">
      <div class="stack intro">
        <div>
          <p class="eyebrow">Chci vyvěsit budky</p>
          <h1>Pověsíme budky spolu</h1>
          <p class="muted lead">
            Napiš nám, kde by budky mohly viset. Ozveme se, domluvíme místo a pomůžeme s
            budkami i s prvním čištěním.
          </p>
        </div>
        <div v-if="sent" class="card stack" data-testid="want-to-hang-sent">
          <h2>Díky, zpráva odešla</h2>
          <p>Ozveme se ti na {{ values.email }}, nejpozději do týdne.</p>
        </div>
        <n-form
          v-else
          ref="form"
          class="card"
          :model="values"
          :rules="rules"
          @submit.prevent="submit"
        >
          <div class="pair">
            <n-form-item
              label="Jméno"
              path="name"
              :feedback="feedback('name')"
              :validation-status="feedback('name') && 'error'"
            >
              <n-input v-model:value="values.name" />
            </n-form-item>
            <n-form-item
              label="E-mail"
              path="email"
              :feedback="feedback('email')"
              :validation-status="feedback('email') && 'error'"
            >
              <n-input v-model:value="values.email" :input-props="{ type: 'email' }" />
            </n-form-item>
          </div>
          <n-form-item label="Telefon (nepovinné)" path="phone">
            <n-input v-model:value="values.phone" placeholder="+420 …" />
          </n-form-item>
          <n-form-item
            label="Kde by budky visely"
            path="place"
            :feedback="feedback('place')"
            :validation-status="feedback('place') && 'error'"
          >
            <div class="with-hint">
              <n-input v-model:value="values.place" />
              <span class="small muted">
                Obec a místo stačí. Přesnou polohu doladíme spolu.
              </span>
            </div>
          </n-form-item>
          <n-form-item label="Kolik budek zhruba" path="box_count">
            <ChoiceChips v-model="values.box_count" :options="BOX_COUNTS" />
          </n-form-item>
          <n-form-item label="Budky" path="box_source">
            <ChoiceChips v-model="values.box_source" :options="BOX_SOURCES" />
          </n-form-item>
          <n-form-item label="Zpráva" path="message">
            <n-input
              v-model:value="values.message"
              type="textarea"
              :autosize="{ minRows: 3 }"
            />
          </n-form-item>
          <div class="row">
            <n-button type="primary" size="large" attr-type="submit" :loading="sending">
              Odeslat
            </n-button>
            <span class="small muted">
              Zprávu dostane hnuti@brontosaurus.cz a koordinátoři budek.
            </span>
          </div>
        </n-form>
      </div>
      <aside class="card stack">
        <h3>Co bude dál</h3>
        <ol class="steps">
          <li v-for="[title, text] in STEPS" :key="title">
            <b>{{ title }}</b> {{ text }}
          </li>
        </ol>
        <div class="note">
          <AppIcon name="book" />
          <div>
            <b>Než začneš</b>
            Brožury Ptačí budky a Výroba ptačích budek mají rozměry i otvory pro každý
            druh.
          </div>
        </div>
      </aside>
    </div>
  </main>
</template>

<style scoped>
.intro {
  gap: 20px;
}

.intro h1 {
  margin-top: 8px;
}

.lead {
  margin-top: 10px;
  font-size: 17px;
  max-width: 52ch;
}

.pair {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  gap: 14px;
}

.with-hint {
  display: grid;
  gap: 4px;
  width: 100%;
}

.steps {
  margin: 0;
  padding-left: 20px;
  display: grid;
  gap: 10px;
}

@media (max-width: 720px) {
  .pair {
    grid-template-columns: minmax(0, 1fr);
    gap: 0;
  }
}
</style>
