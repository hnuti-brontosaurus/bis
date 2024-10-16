import { FC } from 'react'
import { ExternalButtonLink } from 'components'
import { HiExternalLink } from 'react-icons/hi'
import style from './DetailedInstructionsLink.module.scss'

export const DetailedInstructionsLink: FC = () => (
  <ExternalButtonLink
    href="https://drive.google.com/file/d/119C-T4vovVu_AW7X-t8C5GqDaVuH7EhX/view"
    tertiary
    target="__blank"
    rel="noopener noreferrer"
    className={style.link}
  >
    podrobný návod
    <HiExternalLink />
  </ExternalButtonLink>
)
