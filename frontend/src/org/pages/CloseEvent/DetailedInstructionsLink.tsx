import { FC } from 'react'
import { ExternalButtonLink } from 'components'
import { HiExternalLink } from 'react-icons/hi'
import style from './DetailedInstructionsLink.module.scss'

export const DetailedInstructionsLink: FC = () => (
  <ExternalButtonLink
    href="https://www.brontosaurus.cz" // FIXME change link
    tertiary
    target="__blank"
    rel="noopener noreferrer"
    className={style.link}
  >
    podrobný návod
    <HiExternalLink />
  </ExternalButtonLink>
)
