import "@/assets/main.css"

import { createApp } from "vue"

import App from "@/AppProviders.vue"
import router from "@/router.js"

const app = createApp(App)

app.use(router)

router.isReady().then(() => app.mount("#app"))
