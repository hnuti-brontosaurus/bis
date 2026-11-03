import "@/assets/main.css"

import { createApp } from "vue"
import { registerSW } from "virtual:pwa-register"

import App from "@/App.vue"
import router from "@/router.js"
import { pinia } from "@/data/pinia.js"

registerSW({ immediate: true })

createApp(App).use(pinia).use(router).mount("#app")
