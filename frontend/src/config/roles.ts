import { RoleSlug } from 'app/services/bisTypes'

/**
 * Roles with access to administration
 */
export const adminAccessRoles: RoleSlug[] = [
  'director',
  'admin',
  'office_worker',
  'auditor',
  'executive',
  'education_member',
  'chairman',
  'vice_chairman',
  'manager',
  'board_member',
]

/**
 * Roles with access to organizer interface and functionality
 */
export const organizerAccessRoles: RoleSlug[] = [
  'director',
  'admin',
  'office_worker',
  'auditor',
  'executive',
  'education_member',
  'chairman',
  'vice_chairman',
  'manager',
  'board_member',
  'main_organizer',
  'organizer',
  'qualified_organizer',
]

/**
 * Roles with ability to create events without being part of organizer team
 */
export const canCreateEventForOtherOrganizersRoles: RoleSlug[] = [
  'director',
  'admin',
  'office_worker',
  'chairman',
  'vice_chairman',
  'manager',
  'board_member',
]

/**
 * Roles with ability to edit old events, including closed ones
 */
export const canEditOldEventRoles: RoleSlug[] = [
  'director',
  'admin',
  'office_worker',
]
