// This script downloads translations from backend repository
// and generates a module in src/config/static/translations
// You can re-run it with `yarn generate-translations` or `yarn gt` for short
// Also, to run this script you need node v18 or higher because we use node's native fetch

import fs from 'fs/promises'
import { lowerFirst } from 'lodash'
import * as YAML from 'yaml'

type RawModel = {
  name: string
  name_plural: string
  fields: {
    [key: string]: string | string[] | { [key: string]: string }
  }
}

export type Model = Readonly<
  {
    _name: RawModel['name']
    _name_plural: RawModel['name_plural']
  } & RawModel['fields']
>

const generate = async () => {
  const yamlModelTranslations = await (
    await fetch(
      'https://raw.githubusercontent.com/hnuti-brontosaurus/bis/master/backend/translation/model_translations.yaml',
    )
  ).text()

  const yamlStringTranslations = await (
    await fetch(
      'https://raw.githubusercontent.com/hnuti-brontosaurus/bis/master/backend/translation/string_translations.yaml',
    )
  ).text()

  const rawModelTranslations = YAML.parse(yamlModelTranslations)
  const rawStringTranslations = YAML.parse(yamlStringTranslations)

  const modelEntries: [string, Model][] = Object.entries(
    rawModelTranslations,
  ).map(([name, model]) => {
    const raw = model as RawModel
    return [
      lowerFirst(name),
      {
        _name: raw.name,
        _name_plural: raw.name,
        ...raw.fields,
      },
    ]
  })

  const stringEntries: [string, { [key: string]: string }][] = Object.entries(
    rawStringTranslations,
  )

  const initialComment = `
  // This file was automatically generated with a script.
  //
  // !!!DO NOT EDIT!!!
  //
  // You can generate it again with \`yarn generate-translations\` or \`yarn gt\` for short.
  // The script is defined in \`bin/generateTranslations.ts\`


  `

  await fs.writeFile(
    'src/config/static/translations.ts',
    initialComment +
      [...modelEntries, ...stringEntries]
        .map(
          ([name, value]) =>
            `export const ${name} = ${JSON.stringify(value)} as const;\n\n`,
        )
        .join(''),
  )
}

generate()
