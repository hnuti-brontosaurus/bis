import { useAppSelector } from 'app/hooks'
import { selectAuthToken } from 'features/auth/authSlice'
import { useState } from 'react'

/**
 * Export file from api
 * To make request we don't use rtk-query because we don't want to cache the whole file
 * endpoint is made using authenticated GET request to the API
 * @param getUrl - function that accepts params and generates api endpoint URL
 * @param getName - function that accepts params and generates name of exported file
 * @returns function that runs the export, and progress indication
 */
export const useExport = <T>(
  getUrl: (props: T) => string,
  getName: (props: T) => string,
) => {
  const token = useAppSelector(selectAuthToken)
  const [isLoading, setIsLoading] = useState(false)

  const exportFile = async (props: T) => {
    setIsLoading(true)
    const response = await fetch(getUrl(props), {
      // Make request to API endpoint
      method: 'GET',
      headers: { authorization: `Token ${token}` },
    })

    const blob = await response.blob() // Get response data as blob
    const url = globalThis.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url // Set the link's href attribute to the download URL
    link.download = getName(props)

    document.body.appendChild(link) // Add the link to the document body
    link.click() // Click the link to start the download
    document.body.removeChild(link)
    setIsLoading(false)
  }

  return [exportFile, { isLoading }] as const
}
