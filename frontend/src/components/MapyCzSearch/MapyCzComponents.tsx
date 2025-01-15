import { FC, ReactElement } from 'react'
import { components, FormatOptionLabelMeta, MenuProps } from 'react-select'
import styles from './MapyCzComponents.module.scss'

type MenuType = <Option>(Props: MenuProps<Option>) => ReactElement

export const MenuWithAttribution: MenuType = props => (
  <components.Menu {...props}>
    {props.children}
    <div className={styles.attribution}>
      Hledají <img src="https://api.mapy.cz/img/api/logo-small.svg" />
    </div>
  </components.Menu>
)

interface OptionLabelProps {
  name: string
  specific?: string
}

export const OptionLabel: FC<OptionLabelProps> = ({ name, specific }) => (
  <div>
    <div>{name}</div>
    {specific && <div className={styles.specific}>{specific}</div>}
  </div>
)

type CreateOptionLabelType = <Option>(
  getName: (option: Option) => string,
  getSpecific: (option: Option) => string | undefined,
) => (option: Option, meta: FormatOptionLabelMeta<Option>) => ReactElement

export const createOptionLabel: CreateOptionLabelType =
  (getName, getSpecific) =>
  (option, { context }) =>
    (
      <OptionLabel
        name={getName(option)}
        specific={context === 'menu' ? getSpecific(option) : undefined}
      />
    )

export const loadingMessage = () => <>Hledám&hellip;</>

export const noOptionsMessage =
  (inputValue: string, query: string, limit: number) => () => {
    if (inputValue !== query) {
      return <>Čekám až dopíšeš&hellip;</>
    } else if (inputValue.length < limit) {
      return <>Zadej alespoň {limit} znaky</> // TODO correct plurals
    } else {
      return <>Nic jsem nenašel</>
    }
  }
