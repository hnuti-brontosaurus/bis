import type { SerializedError } from '@reduxjs/toolkit'
import type { FetchBaseQueryError } from '@reduxjs/toolkit/query'
import { LoadingIcon } from 'components/LoadingIcon/LoadingIcon'
import { useShowMessage } from 'features/systemMessage/useSystemMessage'
import { useArrayState } from 'hooks/useArrayState'
import { FC } from 'react'
import { apiErrors2Message } from 'utils/apiErrors'
import { file2base64 } from 'utils/helpers'
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

interface Props {
  name: string
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
  name,
  files,
  upload,
  remove,
  colorTheme,
}) => {
  const [pending, addPending, removePending] = useArrayState<File>()
  const showMessage = useShowMessage()

  const uploadAll = async (queue: FileList) => {
    addPending(Array.from(queue))
    for (const file of queue) {
      try {
        await upload(await file2base64(file))
      } catch (error) {
        showMessage({
          type: 'error',
          message: `Soubor ${file.name} se nepodařilo uložit`,
          detail: apiErrors2Message(error as FetchBaseQueryError),
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
      showMessage({
        type: 'error',
        message: 'Soubor se nepodařilo smazat',
        detail: apiErrors2Message(error as FetchBaseQueryError),
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
        <AddImageInput name={name} onAdd={uploadAll} colorTheme={colorTheme} />
      </FileGridItem>
    </FileGrid>
  )
}
