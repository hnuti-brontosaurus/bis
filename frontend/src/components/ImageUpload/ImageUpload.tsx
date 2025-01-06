import classNames from 'classnames'
import forEach from 'lodash/forEach'
import { FC, ReactNode, useEffect } from 'react'
import {
  Controller,
  useFieldArray,
  useFormContext,
  useWatch,
} from 'react-hook-form'
import { FaDownload, FaPencilAlt, FaTimes } from 'react-icons/fa'
import { MdPhotoCamera } from 'react-icons/md'
import { file2base64 } from 'utils/helpers'
import * as messages from 'utils/validationMessages'
import styles from './ImageUpload.module.scss'

export const DownloadLink: FC<{ url: string }> = ({ url }) => {
  const fileName =
    url.match(/filename=(.*?);/)?.[1] ?? url.match(/[^/]*$/)?.[0] ?? ''
  return (
    <a
      href={url}
      download={fileName}
      className={classNames(styles.button, styles.downloadButton)}
    >
      <FaDownload />
    </a>
  )
}

const ImageInput: FC<{ name: string; required?: boolean }> = ({
  name,
  required,
}) => {
  return (
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
  )
}

const ImageAddIcon: FC<{ children: ReactNode; colorTheme?: string }> = ({
  children,
  colorTheme,
}) => (
  <div
    className={classNames(
      styles.addButton,
      colorTheme === 'opportunities' && styles.opportunitiesTheme,
    )}
  >
    <MdPhotoCamera size={60} />
    {children}
  </div>
)

const ImagePreview: FC<{ name: string }> = ({ name }) => {
  const value = useWatch({ name })
  return (
    <div className={styles.imageWrapper}>
      <object data={value} className={styles.image} />
      <div className={styles.editOverlay}>
        <FaPencilAlt size={26} />
      </div>
    </div>
  )
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
    <label tabIndex={0}>
      <ImageInput name={name} required={required} />
      {value ? (
        <ImageThumbnail name={name} thumbnail={thumbnail} />
      ) : (
        <ImageAddIcon colorTheme={colorTheme}>Přidej fotku</ImageAddIcon>
      )}
    </label>
  )
}

export const ImageAdd = ({
  name,
  onAdd,
  colorTheme,
}: {
  name: string
  onAdd: (files: FileList) => void
  colorTheme?: string
}) => (
  <label tabIndex={0}>
    <input
      name={`${name}.add`}
      style={{ display: 'none' }}
      type="file"
      accept="image/*,application/pdf"
      multiple
      onChange={event => event.target.files && onAdd(event.target.files)}
    />
    <ImageAddIcon colorTheme={colorTheme}>Přidej fotky</ImageAddIcon>
  </label>
)

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
    <ul className={styles.imageList}>
      {imageFields.fields.map((item, index) => {
        return (
          <li key={item.id} className={styles.imageItem}>
            <label tabIndex={0}>
              <ImageInput name={`${name}.${index}.${image}`} />
              <ImageThumbnail
                name={`${name}.${index}.${image}`}
                thumbnail={thumbnail && `${name}.${index}.${thumbnail}`}
              />
            </label>
            <div className={styles.toolbar}>
              <DownloadLink url={watch(`${name}.${index}.${image}`)} />
              <button
                className={classNames(styles.button, styles.removeButton)}
                type="button"
                onClick={() => imageFields.remove(index)}
              >
                <FaTimes />
              </button>
            </div>
          </li>
        )
      })}
      <li key="add" className={styles.imageItem}>
        <ImageAdd name={name} onAdd={addImages} colorTheme={colorTheme} />
      </li>
    </ul>
  )
}
