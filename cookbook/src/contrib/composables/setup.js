import axios from "axios"
import { useNotification } from "naive-ui"
import { ConcurrencyManager } from "@/contrib/composables/concurrencyManager.js"
import { useErrorHandler } from "@/contrib/composables/errorHandler.js"
import { getCurrentInstance } from "vue"

export function useSetup() {
  const notification = useNotification()

  function setupAxios() {
    axios.defaults.baseURL = "/api/cookbook"
    ConcurrencyManager(axios, 5)
  }

  function setupErrorHandler() {
    const app = getCurrentInstance().appContext.app

    app.config.errorHandler = (error, instance, info) => {
      console.error("Global error:", error)
      console.log("Vue instance:", instance)
      console.log("Error info:", info)

      notification.error({ title: String(error), content: info })
    }
  }

  return { setupAxios, setupErrorHandler }
}
