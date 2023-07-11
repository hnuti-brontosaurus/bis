import { sanitize } from 'dompurify'
import { createElement } from 'react'
import { Link } from 'react-router-dom'
import { formatDateTime } from 'utils/helpers'
import type {
  GenericTranslations,
  ModelTranslations,
} from 'utils/validationErrors'
import styles from './DataView.module.scss'

type Data =
  | { [key: string]: Data }
  | Data[]
  | number
  | string
  | boolean
  | undefined
  | null

/**
 * This component displays data of a generic object
 * It translates object keys if translation object of a matching shape is provided
 * We don't deal with translations of arrays well
 */
export const DataView = <T extends Data>({
  data,
  translations,
  genericTranslations,
  depth = 0,
}: {
  data: T
  translations?: ModelTranslations
  genericTranslations?: GenericTranslations
  depth?: number
}) => {
  if (
    data === null ||
    data === undefined ||
    (typeof data === 'string' && data.length === 0)
  )
    return null
  if (typeof data === 'boolean') return data ? <>Ano</> : <>Ne</>
  if (typeof data === 'number') return <>{data}</>
  if (typeof data === 'string') {
    // display date
    if (/^\d{4}-\d{1,2}-\d{1,2}$/.test(data)) return <>{formatDateTime(data)}</>
    // display html
    if (/<\/?[a-z][\s\S]*>/i.test(data))
      return (
        <div
          className={styles.withFormattedHTML}
          dangerouslySetInnerHTML={{
            __html: sanitize(data),
          }}
        />
      )
    return <>{data}</>
  }

  // show array as unordered list
  if (Array.isArray(data))
    return (
      <ul>
        {/* we should be able to do better than using index for a key TODO */}
        {data.map((datum, i) => (
          <li key={i}>
            <DataView
              data={datum}
              depth={depth}
              translations={translations}
              genericTranslations={genericTranslations}
            />
          </li>
        ))}
      </ul>
    )

  // special treatment of categories
  if (typeof data === 'object' && 'slug' in data && 'name' in data)
    return <DataView data={data.name} />

  // special treatment of anything with id and name
  if (depth > 0 && typeof data === 'object' && 'id' in data && 'name' in data)
    return <DataView data={data.name} />

  // special treatment of humans (just show display_name)
  if (
    depth > 0 &&
    typeof data === 'object' &&
    'id' in data &&
    'display_name' in data
  )
    return (
      <Link to={`/profil/${data.id}`}>
        <DataView data={data.display_name} />
      </Link>
    )

  // special treatment of images
  if (
    typeof data === 'object' &&
    'small' in data &&
    'medium' in data &&
    'large' in data &&
    'original' in data &&
    typeof data.small === 'string'
  )
    return <img src={data.small} alt="" />

  return (
    <div className={styles.container}>
      {Object.entries(data).map(([key, value]) => {
        if (
          value === null ||
          value === undefined ||
          (typeof value === 'string' && value.length === 0) ||
          // empty array
          (Array.isArray(value) && value.length === 0)
        )
          return null

        if (
          typeof value === 'object' &&
          !('slug' in value && 'name' in value) &&
          !('id' in value && 'name' in value) &&
          !('display_name' in value)
        )
          return (
            <div key={key} className={styles.block}>
              {createElement(
                `h${depth + 2}`,
                {},
                translateKey(key, translations, genericTranslations) + ':',
              )}
              <DataView
                data={value}
                depth={depth + 1}
                translations={deeperTranslations(key, translations)}
                genericTranslations={genericTranslations}
              />
            </div>
          )

        return (
          <div key={key}>
            <span className={styles.inlineTitle}>
              {translateKey(key, translations, genericTranslations)}
            </span>
            :{' '}
            <DataView
              data={value}
              depth={depth + 1}
              translations={deeperTranslations(key, translations)}
              genericTranslations={genericTranslations}
            />
          </div>
        )
      })}
    </div>
  )
}

const translateKey = (
  key: string,
  translations?: ModelTranslations,
  genericTranslations?: GenericTranslations,
): string => {
  if (translations)
    if (key in translations) {
      const value = translations[key]
      if (typeof value === 'string') return value
      if (typeof value === 'object' && '_name' in value && value._name)
        return value._name
      if (Array.isArray(value)) return value[0]
    }

  if (genericTranslations && key in genericTranslations) {
    return genericTranslations[key]
  }

  return key
}

const deeperTranslations = (key: string, translations?: ModelTranslations) => {
  if (
    translations &&
    typeof translations[key] === 'object' &&
    !Array.isArray(translations)
  )
    return translations[key] as ModelTranslations
}
