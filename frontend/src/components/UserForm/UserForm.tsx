/**
 * TODO Missing pronoun field when user edits themself
 */
import { yupResolver } from '@hookform/resolvers/yup'
import { api } from 'app/services/bis'
import { User, UserPayload } from 'app/services/bisTypes'
import {
  Actions,
  BirthdayInput,
  birthdayValidation,
  Button,
  FormInputError,
  FormSection,
  FormSectionGroup,
  FormSubsection,
  FullSizeElement,
  InlineSection,
  Label,
  Loading,
} from 'components'
import * as translations from 'config/static/translations'
import dayjs from 'dayjs'
import { useShowMessage } from 'features/systemMessage/useSystemMessage'
import {
  useClearPersistentForm,
  usePersistentFormData,
  usePersistForm,
} from 'hooks/persistForm'
import { merge, mergeWith, omit, pick, startsWith } from 'lodash'
import { useEffect, useState } from 'react'
import { Controller, FormProvider, useForm } from 'react-hook-form'
import { Optional } from 'utility-types'
import { withOverwriteArray } from 'utils/helpers'
import { validationErrors2Message } from 'utils/validationErrors'
import * as yup from 'yup'

/**
 * Expected fields are defined here:
 * https://docs.google.com/document/d/1hXfz0NhBL8XrUOEJR5VmuoDOwNADxEo3j5gA5knE1GE/edit?usp=drivesdk
 */

export type UserFormShape = Omit<
  Optional<UserPayload, 'pronoun'>,
  'all_emails'
> & {
  isChild?: boolean
}

// transform user data to initial form data
export const data2form = (user: User): UserFormShape => {
  return merge({}, omit(user, 'pronoun', 'address', 'contact_address'), {
    email: user.email ?? '',
    pronoun: user.pronoun?.id ?? 0,
    address: omit(user.address, 'region'),
    contact_address: omit(user.contact_address, 'region'),
    close_person: user.close_person ?? {
      first_name: '',
      last_name: '',
      email: '',
      phone: '',
    },
    health_insurance_company: user.health_insurance_company?.id ?? 0,
    isChild: user.birthday
      ? dayjs().diff(dayjs(user.birthday), 'year') < 15
      : undefined,
  })
}

// transform form data to edit user payload
export const form2payload = (
  data: UserFormShape,
  isSelf = false,
): Partial<UserPayload> => {
  const contact_address =
    data.contact_address?.city &&
    data.contact_address?.street &&
    data.contact_address?.zip_code
      ? data.contact_address
      : null

  const close_person =
    data.close_person?.email ||
    data.close_person?.first_name ||
    data.close_person?.last_name ||
    data.close_person?.phone
      ? data.close_person
      : null

  const finalData: Partial<UserPayload> = merge(
    { eyca_card: null },
    pick(
      data,
      'first_name',
      'last_name',
      'birth_name',
      'nickname',
      'birthday',
      'health_issues',
      'email',
      'phone',
      'subscribed_to_newsletter',
      'address',
      'donor',
      'offers',
      'eyca_card',
    ),
    {
      pronoun: Number(data.pronoun) || null,
      contact_address,
      health_insurance_company: Number(data.health_insurance_company) || null,
      close_person,
    },
  )

  // if email is empty string, set it to null
  // (maybe deleting it would also work)
  if (!finalData.email) finalData.email = null

  if (!isSelf) delete finalData.pronoun

  return finalData
}

// form validation schemata
const addressValidationSchema: yup.ObjectSchema<UserFormShape['address']> = yup
  .object()
  .shape(
    {
      street: yup.string().when(['city', 'zip_code'], {
        is: (city: string, zip: string) => city || zip,
        then: schema => schema.required(),
        otherwise: schema => schema.defined(),
      }),
      city: yup.string().when(['street', 'zip_code'], {
        is: (street: string, zip: string) => street || zip,
        then: schema => schema.required(),
        otherwise: schema => schema.defined(),
      }),
      zip_code: yup.string().when(['street', 'city'], {
        is: (street: string, city: string) => street || city,
        then: schema => schema.required(),
        otherwise: schema => schema.defined(),
      }),
    },
    [
      ['street', 'city'],
      ['street', 'zip_code'],
      ['city', 'zip_code'],
    ],
  )

const validationSchema: yup.ObjectSchema<UserFormShape> = yup.object({
  isChild: yup.boolean().defined(),
  first_name: yup.string().required(),
  last_name: yup.string().required(),
  birth_name: yup.string(),
  nickname: yup.string(),
  birthday: birthdayValidation.required(),
  pronoun: yup.number(), // this is optional - none is 0
  health_insurance_company: yup.number().required(), // this is optional - none is 0
  health_issues: yup.string(),
  email: yup.string().email(),
  // .when('isChild', {
  //   is: true,
  //   then: schema => schema.defined(),
  //   otherwise: schema => schema.required(),
  // }),
  phone: yup.string(),
  subscribed_to_newsletter: yup.boolean().required(),
  address: yup
    .object()
    .shape({
      street: yup.string().required(),
      city: yup.string().required(),
      zip_code: yup.string().required(),
    })
    .required(),
  contact_address: addressValidationSchema,
  // close person is required when is child
  close_person: yup.object().when('isChild', {
    is: true,
    then: schema =>
      schema
        .shape({
          first_name: yup.string().trim().required(),
          last_name: yup.string().trim().required(),
          phone: yup.string().trim().required(),
          email: yup.string().email().required(),
        })
        .required(),
    otherwise: schema =>
      schema
        .shape(
          {
            first_name: yup.string().when(['last_name', 'email', 'phone'], {
              is: (lastName?: string, email?: string, phone?: string) =>
                lastName || email || phone,
              then: schema => schema.required(),
              otherwise: schema => schema.defined(),
            }),
            last_name: yup
              .string()
              .defined()
              .when(['first_name', 'email', 'phone'], {
                is: (firstName?: string, email?: string, phone?: string) =>
                  firstName || email || phone,
                then: schema => schema.required(),
                otherwise: schema => schema.defined(),
              }),
            email: yup.string().email(),
            phone: yup.string(),
          },
          [['first_name', 'last_name']],
        )
        .defined(),
  }),
})

export { validationSchema as userValidationSchema }

export const UserForm = ({
  id,
  initialData,
  isSelf = false,
  onSubmit,
  onCancel,
  validateImmediately,
  loading,
}: {
  // provide id for persisting form data
  // because we don't want to overwrite contexts
  id: string
  isSelf?: boolean
  onSubmit: (data: UserPayload, id?: string) => void
  onCancel: () => void
  initialData?: User
  validateImmediately?: boolean
  loading?: boolean
}) => {
  const showMessage = useShowMessage()

  // fetch data for form
  const { data: pronouns } = api.endpoints.readPronouns.useQuery({})
  const { data: healthInsuranceCompanies } =
    api.endpoints.readHealthInsuranceCompanies.useQuery({ pageSize: 1000 })

  const persistedData = usePersistentFormData('user', id)

  const methods = useForm<UserFormShape>({
    defaultValues: mergeWith(
      {
        health_insurance_company: 0,
        address: { street: '', city: '', zip_code: '' },
        contact_address: { street: '', city: '', zip_code: '' },
        subscribed_to_newsletter: true,
      },
      initialData ? data2form(initialData) : {},
      persistedData,
      withOverwriteArray,
    ),
    resolver: yupResolver(validationSchema),
    mode: validateImmediately ? 'onChange' : undefined,
  })
  const { register, watch, control, trigger, formState, handleSubmit } = methods

  useEffect(() => {
    if (validateImmediately) trigger()
  }, [trigger, validateImmediately])

  usePersistForm('user', id, watch)

  const cancelPersist = useClearPersistentForm('user', id)

  // validate form fields dependent on other fields
  // i wish there was a better way
  // maybe there is, but i haven't found it
  useEffect(() => {
    const subscription = watch((data, { name }) => {
      if (formState.isSubmitted) {
        if (startsWith(name, 'address')) trigger('address')
        if (startsWith(name, 'contact_address')) trigger('contact_address')
        if (startsWith(name, 'close_person')) trigger('close_person')
        if (name === 'isChild') trigger()
      }
    })
    return subscription.unsubscribe
  }, [formState.isSubmitted, trigger, watch])

  const handleFormSubmit = handleSubmit(
    async data => {
      setIsSaving(true)
      try {
        await onSubmit(
          form2payload(data, isSelf) as UserPayload,
          initialData?.id,
        )
        // TODO on success clear the form
        cancelPersist()
      } catch {
        // here we just catch the api error when it appears
        // that's to satisfy cypress tests
      } finally {
        setIsSaving(false)
      }
    },
    errors => {
      showMessage({
        type: 'error',
        message: 'Opravte, prosím, chyby ve validaci',
        detail: validationErrors2Message(
          merge({}, ...Object.values(errors)),
          translations.user,
          translations.generic,
        ),
      })
    },
  )

  const handleFormCancel = () => {
    cancelPersist()
    onCancel()
  }

  const [isSaving, setIsSaving] = useState(false)

  if (!(pronouns && healthInsuranceCompanies))
    return <Loading>Připravujeme formulář</Loading>

  const isChild = watch('isChild')

  return (
    <form onSubmit={handleFormSubmit} onReset={handleFormCancel}>
      <FormProvider {...methods}>
        <FormSectionGroup>
          <InlineSection>
            <Label htmlFor="isChild">Mladší 15 let</Label>
            <FormInputError>
              <input type="checkbox" id="isChild" {...register('isChild')} />
            </FormInputError>
          </InlineSection>
          <FormSection header="Osobní údaje">
            <InlineSection>
              <Label required>Jméno</Label>
              <FormInputError>
                <input type="text" {...register('first_name')} />
              </FormInputError>
            </InlineSection>
            <InlineSection>
              <Label required>Příjmení</Label>
              <FormInputError>
                <input type="text" {...register('last_name')} />
              </FormInputError>
            </InlineSection>
            <InlineSection>
              <Label>Rodné příjmení</Label>
              <FormInputError>
                <input type="text" {...register('birth_name')} />
              </FormInputError>
            </InlineSection>
            <InlineSection>
              <Label>Přezdívka</Label>
              <FormInputError>
                <input type="text" {...register('nickname')} />
              </FormInputError>
            </InlineSection>
            <InlineSection>
              <Label required>Datum narození</Label>
              <FormInputError>
                <Controller
                  control={control}
                  name="birthday"
                  render={({ field }) => <BirthdayInput {...field} />}
                />
              </FormInputError>
            </InlineSection>
            {isSelf && (
              <InlineSection>
                <Label>Oslovení</Label>
                <FormInputError>
                  <select {...register('pronoun')}>
                    <option value={0}>&ndash;&ndash;&ndash;</option>
                    {pronouns.results.map(pronoun => (
                      <option key={pronoun.slug} value={pronoun.id}>
                        {pronoun.name}
                      </option>
                    ))}
                  </select>
                </FormInputError>
              </InlineSection>
            )}
            <InlineSection>
              <Label>Zdravotní pojišťovna</Label>
              <FormInputError>
                <select
                  style={{ width: '100%', maxWidth: '500px' }}
                  {...register('health_insurance_company')}
                >
                  <option value={0}>&ndash;&ndash;&ndash;</option>
                  {healthInsuranceCompanies.results.map(hic => (
                    <option key={hic.slug} value={hic.id}>
                      {hic.name}
                    </option>
                  ))}
                </select>
              </FormInputError>
            </InlineSection>
            <FullSizeElement>
              <Label>Alergie a zdravotní omezení</Label>
              <textarea {...register('health_issues')} />
            </FullSizeElement>
          </FormSection>
          <FormSection header="Kontaktní údaje">
            <InlineSection>
              <Label required={!isChild}>Email</Label>
              <FormInputError>
                <input type="email" {...register('email')} />
              </FormInputError>
            </InlineSection>
            <InlineSection>
              <Label>Telefon</Label>
              <FormInputError>
                <input type="tel" {...register('phone')} />
              </FormInputError>
            </InlineSection>
            <InlineSection>
              <Label htmlFor="subscribed_to_newsletter">
                Posílat newsletter?
              </Label>
              <FormInputError>
                <input
                  type="checkbox"
                  id="subscribed_to_newsletter"
                  {...register('subscribed_to_newsletter')}
                />
              </FormInputError>
            </InlineSection>
            <FormSubsection header="Adresa" required>
              <InlineSection>
                <Label>Ulice a číslo domu</Label>
                <FormInputError>
                  <input type="text" {...register('address.street')} />
                </FormInputError>
              </InlineSection>
              <InlineSection>
                <Label>Obec</Label>
                <FormInputError>
                  <input type="text" {...register('address.city')} />
                </FormInputError>
              </InlineSection>
              <InlineSection>
                <Label>Směrovací číslo</Label>
                <FormInputError>
                  <input type="text" {...register('address.zip_code')} />
                </FormInputError>
              </InlineSection>
            </FormSubsection>
            <FormSubsection header="Kontaktní adresa">
              <InlineSection>
                <Label>Ulice a číslo domu</Label>
                <FormInputError>
                  <input type="text" {...register('contact_address.street')} />
                </FormInputError>
              </InlineSection>
              <InlineSection>
                <Label>Obec</Label>
                <FormInputError>
                  <input type="text" {...register('contact_address.city')} />
                </FormInputError>
              </InlineSection>
              <InlineSection>
                <Label>Směrovací číslo</Label>
                <FormInputError>
                  <input
                    type="text"
                    {...register('contact_address.zip_code')}
                  />
                </FormInputError>
              </InlineSection>
            </FormSubsection>
          </FormSection>
          <FormSection
            header={isChild ? 'Rodič/zákonný zástupce' : 'Blízká osoba'}
            required={isChild}
          >
            <InlineSection>
              <Label required={isChild}>Jméno</Label>
              <FormInputError>
                <input type="text" {...register('close_person.first_name')} />
              </FormInputError>
            </InlineSection>
            <InlineSection>
              <Label required={isChild}>Příjmení</Label>
              <FormInputError>
                <input type="text" {...register('close_person.last_name')} />
              </FormInputError>
            </InlineSection>
            <InlineSection>
              <Label required={isChild}>Email</Label>
              <FormInputError>
                <input type="email" {...register('close_person.email')} />
              </FormInputError>
            </InlineSection>
            <InlineSection>
              <Label required={isChild}>Telefon</Label>
              <FormInputError>
                <input type="tel" {...register('close_person.phone')} />
              </FormInputError>
            </InlineSection>
          </FormSection>
        </FormSectionGroup>
        <Actions>
          <Button secondary type="reset">
            Zrušit
          </Button>
          <Button primary isLoading={isSaving || loading} type="submit">
            Potvrdit
          </Button>
        </Actions>
      </FormProvider>
    </form>
  )
}
