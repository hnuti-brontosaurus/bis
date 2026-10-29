import type { SerializedError } from '@reduxjs/toolkit'
import type { FetchBaseQueryError } from '@reduxjs/toolkit/query'
import { LoadingIcon } from 'components/LoadingIcon/LoadingIcon'
import { useShowApiErrorMessage } from 'features/systemMessage/useSystemMessage'
import { useRef, useState } from 'react'
import { file2base64 } from 'utils/helpers'
import { AddImageInput } from './AddImageInput'
import { FileFallback } from './FileFallback'
import { FileGrid, FileGridItem } from './FileGrid'
import { UploadedFile } from './UploadedFile'
import { FilePreview } from './FilePreview'

export type UploadedFileType = { id: number; url: string; preview?: string }

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
  files: UploadedFileType[] | undefined
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
    <FileGrid>
      {files?.map(file => (
        <FileGridItem key={file.id}>
          <UploadedFile url={file.url} onRemove={() => removeFile(file.id)}>
            <FilePreview url={file.preview ?? file.url} />
          </UploadedFile>
        </FileGridItem>
      ))}
      {pending.map(({ key, file }) => (
        <FileGridItem key={key}>
          <FileFallback Icon={LoadingIcon}>{file.name}</FileFallback>
        </FileGridItem>
      ))}
      <FileGridItem>
        <AddImageInput onAdd={uploadAll} colorTheme={colorTheme} />
      </FileGridItem>
    </FileGrid>
  )
}
