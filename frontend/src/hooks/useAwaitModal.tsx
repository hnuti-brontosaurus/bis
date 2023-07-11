import { StyledModal } from 'components'
import { useCallback, useEffect, useMemo, useState } from 'react'

// T - data that are returned when resolved
// P - additional props of the Child
export const useAwaitModal = <
  T,
  PP extends { [key: string]: unknown },
  P = Omit<PP, 'onResolve' | 'onReject'>,
>(
  Child: (
    props: P & {
      onResolve: (data: T) => void
      onReject: () => void
    },
  ) => JSX.Element,
  options?: {
    title: string
    props: P
  },
) => {
  const [open, setOpen] = useState(false)
  const [title, setTitle] = useState<string | undefined>(options?.title)
  const [props, setProps] = useState<P>(options?.props as P)
  const [editPromise, setEditPromise] = useState<{
    resolve: (data: T) => void
    reject: (reason?: any) => void
    promise: Promise<T>
  }>()

  useEffect(() => {
    setTitle(options?.title)
  }, [options?.title])

  useEffect(() => {
    setProps(options?.props as P)
  }, [options?.props])

  useEffect(() => {
    setTitle(options?.title)
  }, [options?.title])

  const getModalData = useCallback(
    (options?: { title?: string; props?: P }) => {
      if (options?.title) setTitle(options.title)
      if (options?.props) setProps(options.props)

      let res = undefined
      let rej = undefined

      const promise = new Promise<T>((resolve, reject) => {
        res = resolve
        rej = reject
      })

      const p = {
        promise,
        resolve: res as any,
        reject: rej as any,
      }

      setEditPromise(p)
      setOpen(true)

      return promise
    },
    [],
  )

  const handleResolve = useCallback(
    (data: T) => {
      if (editPromise?.resolve) editPromise.resolve(data)
      setOpen(false)
    },
    [editPromise],
  )

  const handleReject = useCallback(() => {
    if (editPromise?.reject) editPromise.reject()
    setOpen(false)
  }, [editPromise])

  const modal = useMemo(
    () => (
      <StyledModal title={title} open={open} onClose={handleReject}>
        <Child {...props} onResolve={handleResolve} onReject={handleReject} />
      </StyledModal>
    ),
    [Child, handleReject, handleResolve, open, props, title],
  )

  return [getModalData, modal] as const
}
