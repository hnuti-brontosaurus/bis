import { Menu, MenuButton, MenuDivider, MenuItem } from '@szhsin/react-menu'
import { RoleCategory } from 'app/services/bisTypes'
import logoMini from 'assets/logo-mini.png'
import logo from 'assets/logo.png'
import classNames from 'classnames'
import { LoadingIcon } from 'components'
import { useCurrentUser } from 'hooks/currentUser'
import { useAllowedToCreateEvent } from 'hooks/useAllowedToCreateEvent'
import { useCurrentAccess } from 'hooks/useCurrentAccess'
import { useLogout } from 'hooks/useLogout'
import { useMemo } from 'react'
import { AiOutlineMenu } from 'react-icons/ai'
import { FaRegUser } from 'react-icons/fa'
import { Link, useNavigate } from 'react-router-dom'
import { AccessConfig, getUserAccesses } from 'utils/roles'
import styles from './Header.module.scss'

export const Header = () => {
  const { data: user, isAuthenticated } = useCurrentUser()
  const logout = useLogout()
  const [canAddEvent] = useAllowedToCreateEvent()
  const navigate = useNavigate()

  // what's the current access
  const [access, setAccess] = useCurrentAccess()

  // get configurations for all user's accesses
  const userAccesses = useMemo(
    () => (user ? getUserAccesses(user) : []),
    [user],
  )

  // get configuration for current access
  const currentAccessConfig = useMemo(() => {
    return userAccesses.find(config => config.slug === access)
  }, [access, userAccesses])

  // switching access
  const handleSwitchAccess = (accessConfig: AccessConfig) => {
    // if we stay within the app, remember the new current access
    if (!accessConfig.external) setAccess(accessConfig.slug)
    // go to the main page of the new access
    navigate(accessConfig.url)
  }

  return (
    <div className={styles.container}>
      <nav className={styles.logoWrapper}>
        <Link to="/" title="Domů">
          <img className={styles.logo} src={logo} alt="Brontosaurus logo" />
          <img
            className={styles.logoMini}
            src={logoMini}
            alt="Brontosaurus logo"
          />
        </Link>
      </nav>
      <div className={styles.spacer}></div>
      {user && access ? (
        <nav>
          <Menu
            menuButton={({ open }) => (
              <MenuButton
                className={classNames(
                  open && styles.menuButtonOpen,
                  styles.menuButton,
                )}
                title={
                  currentAccessConfig?.roles &&
                  getAccessTitle(currentAccessConfig.roles)
                }
              >
                {currentAccessConfig?.name ?? <LoadingIcon />}
              </MenuButton>
            )}
            // align={'center'}
          >
            {userAccesses.map(accessConfig => (
              <MenuItem
                key={accessConfig.slug}
                className={styles.menuItemCustom}
                title={
                  accessConfig?.roles && getAccessTitle(accessConfig.roles)
                }
              >
                <button onClick={() => handleSwitchAccess(accessConfig)}>
                  {accessConfig.name}
                </button>
              </MenuItem>
            ))}
          </Menu>
        </nav>
      ) : null}
      {isAuthenticated ? (
        <nav>
          <Menu
            menuButton={({ open }) => (
              <MenuButton
                className={classNames(
                  open && styles.menuButtonOpen,
                  styles.menuButton,
                )}
                title={`Menu`}
              >
                {' '}
                <AiOutlineMenu fontSize={20} />
                <div className={styles.profileName}>Menu</div>
              </MenuButton>
            )}
            // align={'center'}
          >
            <MenuItem className={styles.menuItemCustom}>
              <Link to="/org/akce/vsechny">Organizované akce</Link>
            </MenuItem>
            {canAddEvent && (
              <MenuItem className={styles.menuItemCustom}>
                <Link to="/org/akce/vytvorit">Vytvořit akci</Link>
              </MenuItem>
            )}
            <MenuDivider />
            <MenuItem className={styles.menuItemCustom}>
              <Link to="/org/prilezitosti">Příležitosti</Link>
            </MenuItem>
            <MenuItem className={styles.menuItemCustom}>
              <Link to="/org/prilezitosti/vytvorit">Vytvořit příležitost</Link>
            </MenuItem>
          </Menu>
        </nav>
      ) : null}
      {user ? (
        <nav>
          <Menu
            menuButton={({ open }) => (
              <MenuButton
                className={classNames(
                  open && styles.menuButtonOpen,
                  styles.menuButton,
                )}
                title={`${user.first_name} ${user.last_name}`}
              >
                {' '}
                <FaRegUser fontSize={18} />
                <div className={styles.profileName}>
                  {user.first_name} {user.last_name}
                </div>
              </MenuButton>
            )}
            align={'end'}
          >
            <MenuItem className={styles.menuItemProfileData}>
              <Link to={`/profil/${user.id}/upravit`}>
                <span className={styles.menuUserInfo}>
                  <span
                    className={styles.menuName}
                  >{`${user.first_name} ${user.last_name}`}</span>
                  <span className={styles.menuEmail}>{user.email}</span>
                </span>
              </Link>
            </MenuItem>
            <MenuDivider />

            <MenuItem className={styles.menuItemCustom}>
              <Link to={`/user/akce/zucastnene`}>Účast na akcích</Link>
            </MenuItem>
            <MenuItem className={styles.menuItemCustom}>
              <Link to={`/user/akce/prihlasene`}>Přihlášení na akce</Link>
            </MenuItem>
            <MenuDivider />
            <MenuItem className={styles.menuItemCustom}>
              <Link to={`/profil`}>Můj profil</Link>
            </MenuItem>
            <MenuItem className={styles.menuItemCustom}>
              <Link to={`/profil/${user.id}/upravit`}>Upravit profil</Link>
            </MenuItem>
            <MenuDivider />

            <MenuItem className={styles.menuItemCustom}>
              <button onClick={() => logout()}>Odhlásit se</button>
            </MenuItem>
          </Menu>
        </nav>
      ) : null}
    </div>
  )
}

const getAccessTitle = (roles: RoleCategory[]) =>
  `Přístup pro Tvé role: ${roles.map(role => role.name).join(', ')}`
