import classNames from 'classnames'
import forEach from 'lodash/forEach'
import { FC, ReactNode } from 'react'
import { Controller, useFieldArray, useFormContext } from 'react-hook-form'
import { FaDownload, FaPencilAlt, FaTimes } from 'react-icons/fa'
import { MdPhotoCamera } from 'react-icons/md'
import { file2base64 } from 'utils/helpers'
import * as messages from 'utils/validationMessages'
import { useShowMessage } from 'features/systemMessage/useSystemMessage'
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

const useUnsupportedHeicMessage = () => {
  const showMessage = useShowMessage()
  return (file: File) =>
    showMessage({
      type: 'error',
      message: `Nelze nahrát ${file.name}`,
      detail: 'Formát HEIC/HEIF není podporovaný.',
    })
}

const ImageInput: FC<{ name: string; required?: boolean }> = ({
  name,
  required,
}) => {
  const showUnsupportedHeicMessage = useUnsupportedHeicMessage()
  return (
    <Controller
      name={name}
      rules={{ required: required && messages.required }}
      render={({ field: { value, onChange, ...field } }) => (
        <input
          {...field}
          style={{ display: 'none' }}
          type="file"
          accept="image/*,application/pdf"
          onChange={async event => {
            const file = event.target.files?.[0]
            if (file && file.type === 'image/heif') {
              showUnsupportedHeicMessage(file)
            } else {
              const value = file ? await file2base64(file) : ''
              onChange(value)
            }
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

export const ImageField: FC<{
  name: string
  colorTheme?: string
  required?: boolean
}> = ({ name, required, colorTheme }) => {
  const { watch } = useFormContext()

  return (
    <label tabIndex={0}>
      <ImageInput name={name} required={required} />
      {watch(name) ? (
        <div className={styles.imageWrapper}>
          <object data={watch(name)} className={styles.image} />
          <div className={styles.editOverlay}>
            <FaPencilAlt size={26} />
          </div>
        </div>
      ) : (
        <ImageAddIcon colorTheme={colorTheme}>Přidej fotku</ImageAddIcon>
      )}
    </label>
  )
}

export const ImageUpload = ({
  name,
  required,
  colorTheme,
}: {
  name: string
  required?: boolean
  colorTheme?: string
}) => {
  return <ImageField name={name} required={required} colorTheme={colorTheme} />
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
  colorTheme,
}: {
  name: string
  image?: string
  colorTheme?: string
}) => {
  const { control, watch } = useFormContext()
  const imageFields = useFieldArray({
    control,
    name,
  })
  const showUnsupportedHeicMessage = useUnsupportedHeicMessage()

  const addImages = (files: FileList) => {
    forEach(files, async file => {
      if (file.type === 'image/heif') {
        showUnsupportedHeicMessage(file)
      } else {
        const value = await file2base64(file)
        imageFields.append({ [image]: value })
      }
    })
  }

  return (
    <ul className={styles.imageList}>
      {imageFields.fields.map((item, index) => {
        return (
          <li key={item.id} className={styles.imageItem}>
            <ImageField
              name={`${name}.${index}.${image}`}
              colorTheme={colorTheme}
            />
            {watch(`${name}.${index}.${image}`) && (
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
            )}
          </li>
        )
      })}
      <li key="add" className={styles.imageItem}>
        <ImageAdd name={name} onAdd={addImages} />
      </li>
    </ul>
  )
}
