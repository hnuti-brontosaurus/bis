import classNames from 'classnames'
import forEach from 'lodash/forEach'
import { ChangeEvent, forwardRef, useState } from 'react'
import { Controller, useFieldArray, useFormContext } from 'react-hook-form'
import { FaPencilAlt, FaTimes } from 'react-icons/fa'
import { MdPhotoCamera } from 'react-icons/md'
import { file2base64 } from 'utils/helpers'
import * as messages from 'utils/validationMessages'
import styles from './ImageUpload.module.scss'

export const UncontrolledImageUpload = forwardRef<
  HTMLInputElement,
  {
    name: string
    value?: string
    onChange: (e: ChangeEvent<HTMLInputElement>) => void
    onBlur: any
    colorTheme?: string
  }
>(({ value, onChange, colorTheme, ...rest }, ref) => {
  const [internalState, setInternalState] = useState<string>('')

  const actualValue = value ?? internalState
  const handleChange = async (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    const value = file ? await file2base64(file) : ''
    setInternalState(value)
    onChange({ ...e, target: { ...e.target, value, type: 'text' } })
  }

  return (
    <label tabIndex={0}>
      <input
        ref={ref}
        style={{ display: 'none' }}
        type="file"
        accept="image/*"
        onChange={handleChange}
        {...rest}
      />
      {actualValue ? (
        <div className={styles.imageWrapper}>
          <img src={actualValue} alt="" className={styles.image} />
          <div className={styles.editOverlay}>
            <FaPencilAlt size={26} />
          </div>
        </div>
      ) : (
        <div
          className={classNames(
            styles.addButton,
            colorTheme === 'opportunities' && styles.opportunitiesTheme,
          )}
        >
          <MdPhotoCamera size={60} />
          Přidej fotku
        </div>
      )}
    </label>
  )
})

export const ImageUpload = ({
  name,
  required,
  colorTheme,
}: {
  name: string
  required?: boolean
  colorTheme?: string
}) => {
  const { control } = useFormContext()

  return (
    <Controller
      name={name}
      rules={{ required: required && messages.required }}
      control={control}
      render={({ field }) => (
        <UncontrolledImageUpload {...field} colorTheme={colorTheme} />
      )}
    />
  )
}

export const ImageAdd = ({
  onAdd,
  colorTheme,
}: {
  onAdd: (files: FileList) => void
  colorTheme?: string
}) => (
  <label tabIndex={0}>
    <input
      style={{ display: 'none' }}
      type="file"
      accept="image/*"
      multiple
      onChange={event => event.target.files && onAdd(event.target.files)}
    />
    <div
      className={classNames(
        styles.addButton,
        colorTheme === 'opportunities' && styles.opportunitiesTheme,
      )}
    >
      <MdPhotoCamera size={60} />
      Přidej fotky
    </div>
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

  const addImages = (files: FileList) => {
    forEach(files, async file => {
      const value = await file2base64(file)
      imageFields.append({ [image]: value })
    })
  }

  return (
    <ul className={styles.imageList}>
      {imageFields.fields.map((item, index) => {
        return (
          <li key={item.id} className={styles.imageItem}>
            <Controller
              name={`${name}.${index}.${image}`}
              control={control}
              render={({ field }) => (
                <UncontrolledImageUpload {...field} colorTheme={colorTheme} />
              )}
            />
            {watch(`${name}.${index}.${image}`) && (
              <button
                className={styles.removeButton}
                type="button"
                onClick={() => imageFields.remove(index)}
              >
                <FaTimes />
              </button>
            )}
          </li>
        )
      })}
      <li key="add" className={styles.imageItem}>
        <ImageAdd onAdd={addImages} />
      </li>
    </ul>
  )
}
