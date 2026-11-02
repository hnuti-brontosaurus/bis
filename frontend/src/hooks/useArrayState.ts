import { useRef, useState } from 'react'

export const useArrayState = <T>() => {
  const [items, updateItems] = useState<{ key: number; item: T }[]>([])
  const counter = useRef(0)

  const add = (item: T | T[]) => {
    const newItems = Array.isArray(item) ? item : [item]
    const keyedItems = newItems.map(item => ({
      key: counter.current++,
      item,
    }))
    updateItems(items => [...items, ...keyedItems])
  }

  const remove = (target: T) => {
    updateItems(items => items.filter(({ item }) => item !== target))
  }

  return [items, add, remove] as const
}
