import "@/assets/main.css"

import { createApp } from "vue"

import App from "@/AppProviders.vue"
import router from "@/router.js"
import { pinia } from "@/data/pinia.js"

const app = createApp(App)

app.use(pinia)
app.use(router)

router.isReady().then(() => app.mount("#app"))
