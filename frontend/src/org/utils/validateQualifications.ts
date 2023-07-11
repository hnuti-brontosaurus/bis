import type {
  Event,
  EventCategory,
  Qualification,
  QualificationCategory,
  User,
} from 'app/services/bisTypes'

export const getRequiredQualifications = (
  event: Partial<Pick<Event, 'intended_for' | 'group' | 'category'>>,
): string[] => {
  const qualificationRequiredForCategories: EventCategory['slug'][] = [
    'internal__general_meeting',
    'internal__section_meeting',
    'public__volunteering',
    'public__only_experiential',
    'public__educational__course',
    'public__educational__ohb',
    'public__other__for_public',
  ]

  const intendedFor = event.intended_for?.slug ?? ''
  const group = event.group?.slug ?? ''
  const category = event.category?.slug ?? ''

  if (
    !qualificationRequiredForCategories.includes(
      category as EventCategory['slug'],
    )
  )
    return []

  let required_one_of: string[] = []

  if (intendedFor === 'for_kids') {
    if (group === 'camp' || category === 'internal__section_meeting')
      required_one_of = ['kids_leader']
    else required_one_of = ['kids_intern']
  }

  if (intendedFor === 'for_parents_with_kids') {
    if (group === 'camp') required_one_of = ['kids_leader', 'organizer']
    if (group === 'weekend_event')
      required_one_of = ['kids_intern', 'weekend_organizer']
  }

  if (
    ['for_all', 'for_young_and_adult', 'for_first_time_participant'].includes(
      intendedFor,
    )
  ) {
    if (group === 'camp') required_one_of = ['organizer']
    if (group === 'weekend_event') required_one_of = ['weekend_organizer']
  }

  if (category === 'public__educational__ohb') required_one_of = ['instructor']

  return required_one_of
}

export const canBeMainOrganizer = (
  event: Partial<Pick<Event, 'intended_for' | 'group' | 'category' | 'start'>>,
  user: User,
  allQualifications: QualificationCategory[],
): boolean => {
  if (!user.birthday) throw new Error('Není znám věk hlavního organizátora')
  const age = getAge(user.birthday)
  if (age < 18) throw new Error('Hlavní organizátor musí mít aspoň 18 let')

  //// turn this on if you want to make sure that organizer is member when organizing...
  // const isMemberWhenOrganized =
  //   user.memberships &&
  //   user.memberships.some(
  //     membership =>
  //       event.start && membership.year === new Date(event.start).getFullYear(),
  //   )
  // if (!isMemberWhenOrganized)
  //   throw new Error(
  //     'Hlavní organizátor musí mít aktivní členství v roce konání akce',
  //   )

  const required_one_of = getRequiredQualifications(event)

  if (required_one_of.length > 0) {
    if (!hasRequiredQualification(user, required_one_of, allQualifications)) {
      const categories = required_one_of
        .map(slug => allQualifications.find(q => q.slug === slug))
        .filter(q => q) as QualificationCategory[]

      throw new Error(
        `Hlavní organizátor ${
          user.display_name
        } musí mít kvalifikaci ${categories
          .map(category => category?.name)
          .join(' nebo ')} nebo kvalifikaci nadřazenou.`,
      )
    }
  }

  return true
}

export const canBeMainOrganizer2: typeof canBeMainOrganizer = (
  event,
  user,
  allQualifications,
) => {
  try {
    return canBeMainOrganizer(event, user, allQualifications)
  } catch (e) {
    return false
  }
}

const getQualificationDict = (qs: QualificationCategory[]) =>
  Object.fromEntries(qs.map(q => [q.id, q]))

const getValidQualifications = (user: User): Qualification[] =>
  user.qualifications.filter(
    qualification =>
      new Date(qualification.valid_since) <= new Date() &&
      new Date() <= new Date(qualification.valid_till),
  )

export const hasRequiredQualification = (
  user: User,
  required_one_of: string[],
  allQualifications: QualificationCategory[],
) => {
  const allQualificationsDict = getQualificationDict(allQualifications)

  // get requiredOneOf as full qualification categories
  // because we'll need to access parent qualification categories, too
  const requiredOneOf = required_one_of.map(slug =>
    allQualifications.find(q => q.slug === slug),
  ) as QualificationCategory[]

  const requiredCategoryIsPresent = (
    category: QualificationCategory,
    requiredOneOf: QualificationCategory[],
  ) => {
    if (!category) return false
    if (requiredOneOf.map(r => r.id).includes(category.id)) {
      return true
    }

    // check within parents of requiredOneOf
    for (const required of requiredOneOf) {
      const requiredParents = required.parents.map(
        id => allQualificationsDict[id],
      )
      if (requiredCategoryIsPresent(category, requiredParents)) return true
    }
    return false
  }

  const qualifications = getValidQualifications(user)
  for (const qualification of qualifications) {
    let category: QualificationCategory | undefined = qualification.category
    if (requiredCategoryIsPresent(category, requiredOneOf)) return true
  }
  return false
}

// https://stackoverflow.com/a/7091965
function getAge(dateString: string): number {
  var today = new Date()
  var birthDate = new Date(dateString)
  var age = today.getFullYear() - birthDate.getFullYear()
  var m = today.getMonth() - birthDate.getMonth()
  if (m < 0 || (m === 0 && today.getDate() < birthDate.getDate())) {
    age--
  }
  return age
}

/*
// https://github.com/lamanchy/bis/blob/master/backend/bis/models.py
@classmethod
def user_has_required_qualification(cls, user, required_one_of):
    qualifications = user.get_qualifications()
    for qualification in qualifications:
        for slug in qualification.category.get_slugs():
            if slug in required_one_of:
                return True

@classmethod
def validate_main_organizer(cls, event, main_organizer: User):
    age = main_organizer.age
    intended_for = event.intended_for.slug
    group = event.group.slug
    category = event.category.slug

    qualification_required_for_categories = {'internal__general_meeting', 'internal__section_meeting',
                                              'public__volunteering', 'public__only_experiential',
                                              'public__sports', 'public__educational__course',
                                              'public__educational__ohb', 'public__other__for_public', }

    if category not in qualification_required_for_categories:
        return

    if not age:
        raise ValidationError('Není znám věk hlavního organizátora')

    if age < 18:
        raise ValidationError('Hlavní organizátor musí mít aspoň 18 let')

    required_one_of = set()

    if intended_for == 'for_kids':
        if group == 'camp' or category == 'internal__section_meeting':
            required_one_of = {'kids_leader'}
        else:
            required_one_of = {'kids_intern'}

    if intended_for == 'for_parents_with_kids':
        if group == 'camp':
            required_one_of = {'kids_leader', 'organizer'}
        if group == 'weekend_event':
            required_one_of = {'kids_intern', 'weekend_organizer'}

    if intended_for in {'for_all', 'for_young_and_adult', 'for_first_time_participant'}:
        if group == 'camp':
            required_one_of = {'organizer'}
        if group == 'weekend_event':
            required_one_of = {'weekend_organizer'}

    if category == 'public__educational__ohb':
        required_one_of = {'instructor', 'consultant_for_kids'}

    if required_one_of:
        if not cls.user_has_required_qualification(main_organizer, required_one_of):
            categories = [str(QualificationCategory.objects.get(slug=slug)) for slug in required_one_of]
            raise ValidationError(f'Hlavní organizátor {main_organizer} musí mít kvalifikaci '
                                  f'{" nebo ".join(categories)} nebo kvalifikací nadřazenou.')
*/
