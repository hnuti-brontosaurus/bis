import "@/assets/main.css"

import { createApp } from "vue"

import App from "@/App.vue"
import router from "@/router.js"
import { pinia } from "@/data/pinia.js"

createApp(App).use(pinia).use(router).mount("#app")
