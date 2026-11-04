<script setup>
import { ref } from "vue"
import { RouterLink, useRoute } from "vue-router"
import { NDrawer, NDrawerContent } from "naive-ui"

import AppIcon from "@/components/app/AppIcon.vue"
import BrandLogo from "@/components/app/BrandLogo.vue"
import ThemeToggle from "@/components/app/ThemeToggle.vue"
import { loginUrl, logoutUrl, useAuthStore } from "@/data/auth.js"

const NAVIGATION = [
  { to: { name: "landing" }, label: "Úvod", routes: ["landing"] },
  {
    to: { name: "areas" },
    label: "Mapa budek",
    routes: ["areas", "area", "box", "check", "batch"],
  },
  { to: { name: "help" }, label: "Jak na budky", routes: ["help", "help_article"] },
  {
    to: { name: "want_to_hang" },
    label: "Chci vyvěsit budky",
    routes: ["want_to_hang"],
  },
]

const route = useRoute()
const auth = useAuthStore()
const menuOpen = ref(false)
</script>

<template>
  <header class="header">
    <RouterLink class="brand" :to="{ name: 'landing' }">
      <BrandLogo />
      <span>
        <b>Budky</b>
        <small class="hide-sm">Hnutí Brontosaurus</small>
      </span>
    </RouterLink>
    <nav class="nav hide-sm">
      <RouterLink
        v-for="item in NAVIGATION"
        :key="item.label"
        :to="item.to"
        :class="{ active: item.routes.includes(route.name) }"
      >
        {{ item.label }}
      </RouterLink>
    </nav>
    <div class="actions">
      <RouterLink
        v-if="auth.isManager"
        class="batches"
        :to="{ name: 'open_batches' }"
        data-testid="open-batches"
      >
        <AppIcon name="link" />
        <span class="hide-sm">Otevřené obchůzky</span>
        <b>{{ auth.openBatchCount }}</b>
      </RouterLink>
      <a
        v-if="auth.isAuthenticated"
        class="avatar hide-sm"
        :href="logoutUrl(route.fullPath)"
        title="Odhlásit se"
      >
        {{ auth.initials }}
      </a>
      <a v-else class="login hide-sm" :href="loginUrl(route.fullPath)">
        <AppIcon name="user" />
        Přihlásit
      </a>
      <ThemeToggle />
      <button
        class="icon-button only-sm"
        type="button"
        aria-label="Menu"
        @click="menuOpen = true"
      >
        <AppIcon name="menu" />
      </button>
    </div>
  </header>
  <n-drawer v-model:show="menuOpen" placement="right" :width="280">
    <n-drawer-content title="Budky" closable>
      <nav class="drawer-nav" @click="menuOpen = false">
        <RouterLink
          v-for="item in NAVIGATION"
          :key="item.label"
          :to="item.to"
          :class="{ active: item.routes.includes(route.name) }"
        >
          {{ item.label }}
        </RouterLink>
        <a v-if="auth.isAuthenticated" :href="logoutUrl(route.fullPath)">Odhlásit se</a>
        <a v-else :href="loginUrl(route.fullPath)">Přihlásit</a>
      </nav>
    </n-drawer-content>
  </n-drawer>
</template>

<style scoped>
.header {
  display: flex;
  align-items: center;
  gap: 18px;
  padding: 12px 24px;
  background: var(--surface);
  color: var(--text);
  border-bottom: 1px solid var(--line);
  position: relative;
  z-index: 3;
  flex: none;
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  line-height: 1.05;
  color: inherit;
  text-decoration: none;
}

.brand b {
  display: block;
  font-size: 21px;
  font-weight: 800;
  letter-spacing: -0.01em;
}

.brand small {
  display: block;
  font-size: 11.5px;
  color: var(--muted);
  margin-top: 2px;
}

.nav {
  display: flex;
  gap: 2px;
}

.nav a {
  padding: 8px 13px;
  color: inherit;
  text-decoration: none;
  font-weight: 600;
}

.nav a.active {
  color: var(--primary-text);
  box-shadow: inset 0 -3px 0 var(--primary);
}

.actions {
  margin-left: auto;
  display: flex;
  gap: 8px;
  align-items: center;
}

.batches,
.login {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  height: 40px;
  border-radius: var(--r-btn);
  border: 1px solid var(--line);
  color: inherit;
  text-decoration: none;
  font-weight: 600;
  font-size: 14px;
}

.batches {
  padding: 0 6px 0 12px;
}

.login {
  padding: 0 14px;
  border-color: var(--line-strong);
}

.batches b {
  min-width: 26px;
  height: 26px;
  border-radius: var(--r-chip);
  display: grid;
  place-items: center;
  background: var(--accent);
  color: var(--accent-ink);
  font-size: 13px;
  font-weight: 800;
}

.avatar {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  background: var(--primary-soft);
  color: var(--primary-text);
  font-weight: 700;
  font-size: 14px;
  text-decoration: none;
}

.drawer-nav {
  display: grid;
  gap: 2px;
}

.drawer-nav a {
  padding: 10px 12px;
  border-radius: var(--r-in);
  color: var(--text);
  text-decoration: none;
  font-weight: 600;
}

.drawer-nav a.active {
  background: var(--primary-soft);
  color: var(--primary-text);
}

@media (max-width: 720px) {
  .header {
    padding: 10px 14px;
    gap: 10px;
  }
}
</style>
