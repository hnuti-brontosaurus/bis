import "@/assets/main.css"

import { createApp } from "vue"
import { registerSW } from "virtual:pwa-register"

import App from "@/App.vue"
import router from "@/router.js"
import { pinia } from "@/data/pinia.js"
import { initSentry } from "@/sentry.js"

registerSW({ immediate: true })

const app = createApp(App)
initSentry(app)
app.use(pinia).use(router).mount("#app")
