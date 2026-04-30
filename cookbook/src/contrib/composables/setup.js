import axios, { AxiosError } from "axios"
import { useNotification } from "naive-ui"
import { getCurrentInstance } from "vue"
import { createSharedComposable } from "@vueuse/core"

let notification

export const useSetup = createSharedComposable(() => {
  notification = useNotification()

  // Surface uncaught component errors as notifications.
  const app = getCurrentInstance().appContext.app
  app.config.errorHandler = (error, instance, info) => {
    console.error("Global error:", error, instance, info)
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

    if (reason instanceof AxiosError && reason.response?.data) {
      obj = reason.response.data
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
