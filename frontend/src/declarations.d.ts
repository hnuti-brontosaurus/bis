declare module '@changey/react-leaflet-markercluster'

declare module 'react-tooltip-lite' {
  import { ReactNode } from 'react'
  import { TooltipProps as Props } from 'react-tooltip-lite'

  export interface TooltipProps extends Props {
    children: ReactNode
  }
}

// to be able to import excel templates
declare module '*.xlsx'
// to be able to import pdf
declare module '*.pdf'

// SVG imported as URL: import url from 'icon.svg'
declare module '*.svg' {
  const src: string
  export default src
}

// SVG imported as React component: import Icon from 'icon.svg?react'
declare module '*.svg?react' {
  import * as React from 'react'
  const ReactComponent: React.FunctionComponent<
    React.SVGProps<SVGSVGElement> & { title?: string }
  >
  export default ReactComponent
}
