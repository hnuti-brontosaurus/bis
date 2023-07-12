import type { HomeButtonConfig } from 'components'
import { Home as HomeNav } from 'components'
import { useTitle } from 'hooks/title'
import { useAllowedToCreateEvent } from 'hooks/useAllowedToCreateEvent'
import { merge } from 'lodash'
import { useMemo } from 'react'

const buttons: HomeButtonConfig[] = [
  {
    title: 'Nová akce',
    detail: '',
    link: '/org/akce/vytvorit',
    theme: 'createEvent',
  },
  {
    title: 'Akce',
    detail: 'Upravit akci',
    link: '/org/akce/vsechny',
    theme: 'editEvent',
  },
  {
    title: 'Po akci',
    detail: 'Přidat účastníky a evidenci práce',
    link: '/org/akce/nevyplnene',
    theme: 'closeEvent',
  },
  {
    title: 'Příležitosti',
    detail: '',
    link: '/org/prilezitosti',
    theme: 'opportunities',
  },
]

export const Home = () => {
  useTitle('Organizátorský přístup')
  const [canCreateEvent] = useAllowedToCreateEvent()
  const processedButtons = useMemo(() => {
    if (canCreateEvent) {
      return buttons
    } else return merge([], buttons, [{ link: '' }])
  }, [canCreateEvent])
  return <HomeNav buttons={processedButtons} />
}
