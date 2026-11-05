<script setup>
import { reactive, ref } from "vue"
import { NButton, NForm, NFormItem, NInput } from "naive-ui"

import AppIcon from "@/components/app/AppIcon.vue"
import VolunteerHeader from "@/components/app/VolunteerHeader.vue"
import OfflineProgress from "@/components/link/OfflineProgress.vue"
import { useLinkStore } from "@/data/link.js"

const link = useLinkStore()

const form = ref(null)
const values = reactive({ ...link.profile })

const rules = {
  nickname: { required: true, message: "Napiš, jak ti máme říkat.", trigger: "blur" },
  email: [
    {
      required: true,
      message: "Bez e-mailu se tě správce nemůže na nic zeptat.",
      trigger: "blur",
    },
    { type: "email", message: "Tohle nevypadá jako e-mail.", trigger: "blur" },
  ],
}

const submit = () =>
  form.value.validate().then(
    () =>
      (link.profile = { nickname: values.nickname.trim(), email: values.email.trim() }),
    () => {},
  )
</script>

<template>
  <VolunteerHeader
    :title="link.payload.area.name"
    :subtitle="link.payload.batch.name"
    :pending="link.pending"
  />
  <main class="page welcome">
    <div class="stack">
      <p class="eyebrow">{{ link.payload.batch.name }}</p>
      <h1>Díky, že jdeš čistit budky</h1>
      <p class="muted lead">
        Budky v oblasti {{ link.payload.area.name }} čistí
        {{ link.payload.batch.cleaned_by.abbreviation }}. Než vyrazíš, řekni nám, kdo
        jsi. Zeptáme se jen jednou, telefon si to zapamatuje.
      </p>
    </div>
    <n-form
      ref="form"
      class="card"
      :model="values"
      :rules="rules"
      @submit.prevent="submit"
    >
      <n-form-item
        label="Přezdívka"
        path="nickname"
        :label-props="{ for: 'volunteer-nickname' }"
      >
        <n-input
          v-model:value="values.nickname"
          :maxlength="63"
          placeholder="Jak ti říkají"
          :input-props="{ id: 'volunteer-nickname' }"
        />
      </n-form-item>
      <n-form-item
        label="E-mail"
        path="email"
        :label-props="{ for: 'volunteer-email' }"
      >
        <div class="with-hint">
          <n-input
            v-model:value="values.email"
            placeholder="tvuj@email.cz"
            :input-props="{ id: 'volunteer-email', type: 'email' }"
          />
          <span class="small muted">
            Uvidí ho jen správci oblasti, kdyby se na něco potřebovali zeptat.
          </span>
        </div>
      </n-form-item>
    </n-form>
    <OfflineProgress class="card" />
    <n-button type="primary" size="large" block icon-placement="right" @click="submit">
      Pokračovat na mapu
      <template #icon><AppIcon name="chev" /></template>
    </n-button>
    <p class="small muted tip">
      Tip: přidej si stránku na plochu, otevře se jako aplikace.
    </p>
  </main>
</template>

<style scoped>
.welcome {
  max-width: 640px;
  gap: 20px;
}

.lead {
  font-size: 17px;
}

.with-hint {
  display: grid;
  gap: 6px;
  width: 100%;
}

.tip {
  text-align: center;
}
</style>
