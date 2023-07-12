import { useEffect, useState } from 'react'

/**
Inspired by, and mostly copied from npm library `react-mapycz`
It provides SMap of https://api.mapy.cz
https://github.com/flsy/react-mapycz/blob/master/src/hooks.ts

MIT License

Copyright (c) 2020 Falsy

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
 */
export const useSMap = () => {
  const [SMap, setSMap] = useState<[any, boolean]>([undefined, true])
  useEffect(() => {
    const onload = () => {
      // @ts-ignore
      window.Loader.async = true
      // @ts-ignore
      window.Loader.load(null, { suggest: true }, () => {
        // @ts-ignore
        const smap = window.SMap
        // @ts-ignore
        setSMap([smap, false])
      })
    }

    const script = document.createElement('script')
    script.src = 'https://api.mapy.cz/loader.js'
    script.async = true
    script.onload = onload
    document.body.appendChild(script)

    return () => {
      document.body.removeChild(script)
    }
  }, [])

  return SMap
}
