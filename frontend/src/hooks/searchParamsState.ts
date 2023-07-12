import { useSearchParams } from 'react-router-dom'

export const useSearchParamsState = <T extends string | number>(
  key: string,
  defaultValue: T,
  parse: (rawValue: string) => T,
) => {
  const [searchParams, setSearchParams] = useSearchParams()

  const setParam = (param: T) => {
    setSearchParams({
      ...Object.fromEntries(searchParams.entries()),
      [key]: String(param),
    })
  }

  const rawParam = searchParams.get(key)
  const param = rawParam ? parse(rawParam) : defaultValue

  return [param, setParam] as const
}
