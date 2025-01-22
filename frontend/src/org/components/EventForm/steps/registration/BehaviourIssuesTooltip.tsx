import { User } from 'app/services/bisTypes'
import { FC } from 'react'
import { IoWarning } from 'react-icons/io5'
import Tooltip from 'react-tooltip-lite'

import style from './BehaviourIssuesTooltip.module.scss'

interface Props {
  user?: User
}

export const BehaviourIssuesTooltip: FC<Props> = ({ user }) =>
  user?.behaviour_issues ? (
    <Tooltip
      useDefaultStyles
      content={user.behaviour_issues}
      tagName="span"
      className={style.main}
    >
      <IoWarning />
    </Tooltip>
  ) : null
