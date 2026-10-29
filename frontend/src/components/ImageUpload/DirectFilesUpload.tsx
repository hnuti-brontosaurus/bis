import type { SerializedError } from '@reduxjs/toolkit'
import type { FetchBaseQueryError } from '@reduxjs/toolkit/query'
import { LoadingIcon } from 'components/LoadingIcon/LoadingIcon'
import { useShowApiErrorMessage } from 'features/systemMessage/useSystemMessage'
import { FC, useState } from 'react'
import { file2base64 } from 'utils/helpers'
import { useArrayState } from '../../hooks/useArrayState'
import { AddImageInput } from './AddImageInput'
import { FileFallback } from './FileFallback'
import { FileGrid, FileGridItem } from './FileGrid'
import { FilePreview } from './FilePreview'
import { UploadedFile } from './UploadedFile'

export interface UploadedFileType {
  id: number
  url: string
  preview?: string
}

interface Failure {
  error: FetchBaseQueryError | SerializedError
  message: string
}

interface Props {
  files: UploadedFileType[] | undefined
  upload: (file: string) => Promise<unknown>
  remove: (id: number) => Promise<unknown>
  colorTheme?: string
}

/**
 * Saves each file on the server as soon as it is picked, one at a time, so
 * the browser never holds more than one of them as base64.
 */
export const DirectFilesUpload: FC<Props> = ({
  files,
  upload,
  remove,
  colorTheme,
}) => {
  const [pending, addPending, removePending] = useArrayState<File>()
  const [failure, setFailure] = useState<Failure>()
  useShowApiErrorMessage(failure?.error, failure?.message)

  const uploadAll = async (queue: FileList) => {
    addPending(Array.from(queue))
    for (const file of queue) {
      try {
        await upload(await file2base64(file))
      } catch (error) {
        setFailure({
          error: error as Failure['error'],
          message: `Soubor ${file.name} se nepodařilo uložit`,
        })
      } finally {
        removePending(file)
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
          <UploadedFile
            downloadUrl={file.url}
            onRemove={() => removeFile(file.id)}
          >
            <FilePreview url={file.preview ?? file.url} />
          </UploadedFile>
        </FileGridItem>
      ))}
      {pending.map(({ key, item }) => (
        <FileGridItem key={key}>
          <FileFallback Icon={LoadingIcon}>{item.name}</FileFallback>
        </FileGridItem>
      ))}
      <FileGridItem>
        <AddImageInput onAdd={uploadAll} colorTheme={colorTheme} />
      </FileGridItem>
    </FileGrid>
  )
}
