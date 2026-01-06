import axios, { AxiosError } from "axios"
import { useNotification } from "naive-ui"
import { ConcurrencyManager } from "@/contrib/composables/concurrencyManager.js"
import { getCurrentInstance } from "vue"
import { createSharedComposable } from "@vueuse/core"
import { me } from "@/composables/auth.js"

let notification

export const useSetup = createSharedComposable(() => {
  notification = useNotification()

  // setup axios
  axios.defaults.baseURL = "/api/cookbook"
  ConcurrencyManager(axios, 5)

  axios.interceptors.request.use(
    config => {
      if (me.value.user?.token)
        config.headers["Authorization"] = `Token ${me.value.user.token}`
      return config
    },
    error => {
      return Promise.reject(error)
    },
  )

  // setup error handler
  const app = getCurrentInstance().appContext.app

  app.config.errorHandler = (error, instance, info) => {
    console.error("Global error:", error)
    console.log("Vue instance:", instance)
    console.log("Error info:", info)

    notification.error({ title: String(error), content: info })
  }
})

export const handleAxiosError = message => reason => {
  if (axios.isCancel(reason)) return
  handleError(message, reason)
}

export const handleError = (message, reason, obj = undefined) => {
  let params = {
    title: message,
    description: "",
    content: "",
    meta: new Date().toISOString(),
    duration: 3000,
    keepAliveOnHover: true,
  }

  if (reason instanceof Error) {
    setTimeout(() => {
      throw reason
    })
    params.description = reason.message

    if (reason instanceof AxiosError) {
      if (reason.response?.data) {
        obj = reason.response.data
      }
    }
  } else {
    obj = reason
  }

  if (obj) {
    params.content = JSON.stringify(obj, null, 2)
  }

  if (notification) notification.error(params)
  else console.error(params)
}
