import type { SerializedError } from '@reduxjs/toolkit'
import type { FetchBaseQueryError } from '@reduxjs/toolkit/query'
import { LoadingIcon } from 'components/LoadingIcon/LoadingIcon'
import { useShowApiErrorMessage } from 'features/systemMessage/useSystemMessage'
import { useRef, useState } from 'react'
import { file2base64 } from 'utils/helpers'
import { AddImageInput } from './AddImageInput'
import { FileFallback } from './FileFallback'
import { FileGrid } from './FileGrid'
import { FileGridItem } from './FileGridItem'
import { FilePreview } from './FilePreview'
import styles from './ImageUpload.module.scss'

export type UploadedFile = { id: number; url: string; preview?: string }

type Failure = {
  error: FetchBaseQueryError | SerializedError
  message: string
}

/**
 * Saves each file on the server as soon as it is picked, one at a time, so
 * the browser never holds more than one of them as base64.
 */
export const FilesUpload = ({
  name,
  files,
  upload,
  remove,
  colorTheme,
}: {
  name: string
  files: UploadedFile[] | undefined
  upload: (file: string) => Promise<unknown>
  remove: (id: number) => Promise<unknown>
  colorTheme?: string
}) => {
  const [pending, setPending] = useState<{ key: number; file: File }[]>([])
  const nextPendingKey = useRef(0)
  const [failure, setFailure] = useState<Failure>()
  useShowApiErrorMessage(failure?.error, failure?.message)

  const uploadAll = async (fileList: FileList) => {
    const queue = Array.from(fileList, file => ({
      key: nextPendingKey.current++,
      file,
    }))
    setPending(pending => [...pending, ...queue])
    for (const item of queue) {
      try {
        await upload(await file2base64(item.file))
      } catch (error) {
        setFailure({
          error: error as Failure['error'],
          message: `Soubor ${item.file.name} se nepodařilo uložit`,
        })
      } finally {
        setPending(pending => pending.filter(other => other !== item))
      }
    }
  }

  const removeFile = async (id: number) => {
    try {
      await remove(id)
    } catch (error) {
      setFailure({
        error: error as Failure['error'],
        message: 'Soubor se nepodařilo smazat',
      })
    }
  }

  return (
    <FileGrid add={<AddImageInput onAdd={uploadAll} colorTheme={colorTheme} />}>
      {files?.map(file => (
        <FileGridItem
          key={file.id}
          url={file.url}
          onRemove={() => removeFile(file.id)}
        >
          <FilePreview url={file.preview ?? file.url} />
        </FileGridItem>
      ))}
      {pending.map(({ key, file }) => (
        <li key={key} className={styles.imageItem}>
          <FileFallback Icon={LoadingIcon}>{file.name}</FileFallback>
        </li>
      ))}
    </FileGrid>
  )
}
