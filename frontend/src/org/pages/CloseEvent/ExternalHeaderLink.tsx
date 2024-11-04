import { FC, ReactNode } from 'react'
import { ExternalButtonLink } from 'components'
import { HiExternalLink } from 'react-icons/hi'
import style from './ExternalHeaderLink.module.scss'

interface Props {
  href: string
  children: ReactNode
}

export const ExternalHeaderLink: FC<Props> = ({ href, children }) => (
  <ExternalButtonLink
    href={href}
    tertiary
    target="__blank"
    rel="noopener noreferrer"
    className={style.link}
  >
    {children}
    <HiExternalLink />
  </ExternalButtonLink>
)
