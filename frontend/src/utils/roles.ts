import { RoleCategory, RoleSlug, User } from 'app/services/bisTypes'
import {
  adminAccessRoles,
  canCreateEventForOtherOrganizersRoles,
  canEditOldEventRoles,
  organizerAccessRoles,
} from 'config/roles'
import { cloneDeep, intersection } from 'lodash'

export type AccessSlug = 'organizer' | 'admin' | 'user'

export type AccessConfig = {
  slug: AccessSlug
  name: string
  url: string
  external?: boolean
  roles?: RoleCategory[]
}

/**
 * list of available access configurations
 * this can be expanded if other accesses are added
 */
const accessConfigs: Record<AccessSlug, AccessConfig> = {
  admin: { slug: 'admin', name: 'Administrace', url: '/admin', external: true },
  organizer: { slug: 'organizer', name: 'Organizátor/ka', url: '/org' },
  user: { slug: 'user', name: 'Uživatel/ka', url: '/user' },
}

/**
 * extract all role slugs of user
 */
const getUserRoleSlugs = (user: Pick<User, 'roles'>): RoleSlug[] =>
  user.roles.map(role => role.slug as RoleSlug)

/**
 * extract roles (objects) of user that contribute to their admin access
 */
const getUserAdminRoles = (user: Pick<User, 'roles'>): RoleCategory[] =>
  user.roles.filter(role => adminAccessRoles.includes(role.slug))

/**
 * extract roles (objects) of user that contribute to their organizer access
 */
const getUserOrganizerRoles = (user: Pick<User, 'roles'>): RoleCategory[] =>
  user.roles.filter(role => organizerAccessRoles.includes(role.slug))

/**
 * Check whether current user has access to administration interface
 * @param user
 * @returns boolean
 */
export const hasUserAdminAccess = (user: Pick<User, 'roles'>): boolean =>
  intersection(getUserRoleSlugs(user), adminAccessRoles).length > 0

/**
 * Check whether current user has access to organizer interface
 * @param user
 * @returns boolean
 */
export const hasUserOrganizerAccess = (user: Pick<User, 'roles'>): boolean =>
  intersection(getUserRoleSlugs(user), organizerAccessRoles).length > 0

/**
 * Check whether user is allowed to save events when they're not in team
 * @param user
 * @returns boolean
 */
export const canUserSaveEventForOtherOrganizer = (
  user: Pick<User, 'roles'>,
): boolean =>
  intersection(getUserRoleSlugs(user), canCreateEventForOtherOrganizersRoles)
    .length > 0

/**
 * Check whether user is allowed to save events from deeper past (closed events)
 * @param user
 * @returns boolean
 */
export const canUserSaveOldEvent = (user: Pick<User, 'roles'>): boolean =>
  intersection(getUserRoleSlugs(user), canEditOldEventRoles).length > 0

/**
 * Get accesses of the provided user
 * @param user
 * @returns AccessSlug[]
 */
export const getUserAccessOptions = (
  user: Pick<User, 'roles'>,
): AccessSlug[] => {
  const slugs: AccessSlug[] = []

  if (hasUserAdminAccess(user)) slugs.push('admin')
  if (hasUserOrganizerAccess(user)) slugs.push('organizer')
  else slugs.push('user')

  return slugs
}

/**
 * Get default access for the provided user
 * This is useful to set a role after sign-in
 * @param user
 * @returns AccessSlug
 */
export const getUserDefaultAccess = (user: Pick<User, 'roles'>): AccessSlug =>
  hasUserOrganizerAccess(user) ? 'organizer' : 'user'

/**
 * Get configuration of accesses for the provided user
 * This is useful especially for switching accesses and related components
 * For example access switch menu in header
 * @param user
 * @returns AccessConfig[]
 */
export const getUserAccesses = (user: Pick<User, 'roles'>) =>
  getUserAccessOptions(user).map(access => {
    const config = cloneDeep(accessConfigs[access])

    if (access === 'admin') config.roles = getUserAdminRoles(user)
    if (access === 'organizer') config.roles = getUserOrganizerRoles(user)

    return config
  })
