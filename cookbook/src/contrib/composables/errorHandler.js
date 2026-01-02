import { AxiosError } from "axios"
import { useNotification } from "naive-ui"

export function useErrorHandler() {
  const notification = useNotification()
  const handleAxiosError = message => reason => handleError(message, reason)

  function handleError(message, reason, obj = undefined) {
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
    }

    if (obj) {
      params.content = JSON.stringify(obj, null, 2)
    }

    notification.error(params)
  }

  return { handleError, handleAxiosError }
}
