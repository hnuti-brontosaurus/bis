import {
  EndpointDefinitions,
  QueryDefinition,
  skipToken,
} from '@reduxjs/toolkit/dist/query'
import { ApiEndpointQuery } from '@reduxjs/toolkit/dist/query/core/module'
import { QueryHooks } from '@reduxjs/toolkit/dist/query/react/buildHooks'
import type { PaginatedList } from 'app/services/bisTypes'
import { useEffect, useState } from 'react'
import type { Overwrite } from 'utility-types'
import { toDataURL } from 'utils/helpers'

export const useBase64Images = <
  I extends { image: { original: string } },
  T,
  Q extends QueryDefinition<T, any, any, PaginatedList<I>, any>,
  D extends EndpointDefinitions,
>(
  query: ApiEndpointQuery<Q, D> & QueryHooks<Q>,
  param: T,
) => {
  const { data: images, ...state } = query.useQuery((param as any) ?? skipToken)

  const [base64Images, setBase64Images] =
    useState<Overwrite<I, { image: string }>[]>()
  const [isConverting, setIsConverting] = useState(false)

  useEffect(() => {
    ;(async () => {
      if (images && images.results) {
        setIsConverting(true)
        setIsConverting(false)

        const base64Images = await Promise.all(
          images.results
            .filter(({ image }) => image)
            .map(async ({ image, ...rest }) => ({
              ...rest,
              image: await toDataURL(image.original),
            })),
        )

        setBase64Images(base64Images)
      }
    })()
  }, [images])

  return { data: base64Images, isConverting, ...state }
}
