import forEach from 'lodash/forEach'
import { FC, ReactNode, useEffect } from 'react'
import {
  Controller,
  useFieldArray,
  useFormContext,
  useWatch,
} from 'react-hook-form'
import { file2base64 } from 'utils/helpers'
import * as messages from 'utils/validationMessages'
import { AddImageButton } from './AddImageButton'
import { AddImageInput } from './AddImageInput'
import { FileGrid, FileGridItem } from './FileGrid'
import { UploadedFile } from './UploadedFile'
import { FilePreview } from './FilePreview'

interface ImageInputProps {
  name: string
  required?: boolean
  children: ReactNode
}

const ImageInput: FC<ImageInputProps> = ({ name, required, children }) => (
  <label tabIndex={0}>
    <Controller
      name={name}
      rules={{ required: required && messages.required }}
      render={({ field: { value, onChange, ...field } }) => (
        /* cannot set value to file input, throws error */
        <input
          {...field}
          style={{ display: 'none' }}
          type="file"
          accept="image/*,application/pdf"
          onChange={async event => {
            const file = event.target.files?.[0]
            const value = file ? await file2base64(file) : ''
            onChange(value)
          }}
        />
      )}
    />
    {children}
  </label>
)

const ImagePreview: FC<{ name: string }> = ({ name }) => {
  const value = useWatch({ name })
  return <FilePreview url={value} editable />
}

const ImageThumbnail: FC<{ name: string; thumbnail?: string }> = ({
  name,
  thumbnail,
}) => {
  const value = useWatch({ name })
  const { formState, setValue, getFieldState } = useFormContext()
  useEffect(() => {
    if (thumbnail && getFieldState(name, formState).isDirty) {
      setValue(thumbnail, value)
    }
  }, [value, setValue, formState, thumbnail, name, getFieldState])

  return <ImagePreview name={thumbnail ?? name} />
}

export const ImageUpload = ({
  name,
  thumbnail,
  required,
  colorTheme,
}: {
  name: string
  thumbnail?: string
  required?: boolean
  colorTheme?: string
}) => {
  const value = useWatch({ name })
  return (
    <ImageInput name={name} required={required}>
      {value ? (
        <ImageThumbnail name={name} thumbnail={thumbnail} />
      ) : (
        <AddImageButton colorTheme={colorTheme}>Přidej fotku</AddImageButton>
      )}
    </ImageInput>
  )
}

export const ImagesUpload = ({
  name,
  image = 'image',
  thumbnail,
  colorTheme,
}: {
  name: string
  image?: string
  thumbnail?: string
  colorTheme?: string
}) => {
  const { control, watch } = useFormContext()
  const imageFields = useFieldArray({
    control,
    name,
  })

  const addImages = (files: FileList) => {
    forEach(files, async file => {
      const value = await file2base64(file)
      const field = { [image]: value }
      thumbnail && (field[thumbnail] = value)
      imageFields.append(field)
    })
  }

  return (
    <FileGrid>
      {imageFields.fields.map((item, index) => (
        <FileGridItem key={item.id}>
          <UploadedFile
            downloadUrl={watch(`${name}.${index}.${image}`)}
            onRemove={() => imageFields.remove(index)}
          >
            <ImageInput name={`${name}.${index}.${image}`}>
              <ImageThumbnail
                name={`${name}.${index}.${image}`}
                thumbnail={thumbnail && `${name}.${index}.${thumbnail}`}
              />
            </ImageInput>
          </UploadedFile>
        </FileGridItem>
      ))}
      <FileGridItem>
        <AddImageInput
          name={`${name}.add`}
          onAdd={addImages}
          colorTheme={colorTheme}
        />
      </FileGridItem>
    </FileGrid>
  )
}
