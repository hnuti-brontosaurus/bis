import { GuideOwl } from 'components'
import React, { Suspense } from 'react'

const QualificationGuideDownload = React.lazy(
  () => import('./QualificationGuideDownload'),
)

export const QualificationGuide = () => {
  return (
    <GuideOwl id="qualification-guide" left>
      Jakou kvalifikaci musí mít hlavní organizátor/ka?
      <p>
        <Suspense fallback="Načítám">
          <QualificationGuideDownload>Číst průvodce</QualificationGuideDownload>
        </Suspense>
      </p>
    </GuideOwl>
  )
}
