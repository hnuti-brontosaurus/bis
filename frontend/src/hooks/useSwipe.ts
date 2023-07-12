import { useCallback, useEffect, useRef, useState } from 'react'

interface SwipeOptions {
  minDistance?: number
  allowDiagonal?: boolean
  ignoredClass?: string
}

export const useSwipe = (
  onSwipe: (direction: string) => void,
  options?: SwipeOptions,
) => {
  const ref = useRef<HTMLDivElement>(null)
  const [xDown, setXDown] = useState<number>()
  const [yDown, setYDown] = useState<number>()
  const {
    minDistance = 120,
    allowDiagonal = false,
    ignoredClass = 'is-swipe-ignored',
  } = options || {}

  const handleTouchStart = useCallback(
    (event: TouchEvent) => {
      const target = event.target as HTMLElement
      if (target?.classList.contains(ignoredClass)) {
        return
      }
      setXDown(event.touches[0].clientX)
      setYDown(event.touches[0].clientY)
    },
    [ignoredClass],
  )

  const handleTouchMove = useCallback(
    (event: TouchEvent) => {
      const target = event.target as HTMLElement

      if (target?.classList.contains(ignoredClass)) {
        return
      }
      if (!xDown || !yDown) {
        return
      }

      const xUp = event.touches[0].clientX
      const yUp = event.touches[0].clientY

      const xDiff = xDown - xUp
      const yDiff = yDown - yUp

      if (Math.abs(xDiff) < minDistance) {
        return
      }
      if (!allowDiagonal && 20 < Math.abs(yDiff)) {
        return
      }

      if (Math.abs(xDiff) > Math.abs(yDiff)) {
        /*most significant*/
        if (xDiff > 0) {
          /* left swipe */
          onSwipe('left')
        } else {
          /* right swipe */
          onSwipe('right')
        }
      } else {
        if (yDiff > 0) {
          /* up swipe */
          onSwipe('up')
        } else {
          /* down swipe */
          onSwipe('down')
        }
      }
      /* reset values */
      setXDown(undefined)
      setYDown(undefined)
    },
    [onSwipe, minDistance, allowDiagonal, xDown, yDown, ignoredClass],
  )

  useEffect(() => {
    const element = ref.current
    if (!element) return
    element.addEventListener('touchstart', handleTouchStart, false)
    element.addEventListener('touchmove', handleTouchMove, false)

    return () => {
      element.removeEventListener('touchstart', handleTouchStart, false)
      element.removeEventListener('touchmove', handleTouchMove, false)
    }
  }, [handleTouchStart, handleTouchMove])

  return ref
}
