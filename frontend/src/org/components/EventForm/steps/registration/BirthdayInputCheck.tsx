import { yupResolver } from '@hookform/resolvers/yup'
import { FetchBaseQueryError } from '@reduxjs/toolkit/dist/query'
import { User, UserSearch } from 'app/services/bisTypes'
import {
  BirthdayInput,
  birthdayValidation,
  Button,
  ErrorBox,
  FormInputError,
  InlineSection,
  Label,
  ObjectWithStrings,
} from 'components'
import { FC } from 'react'
import { Controller, useForm } from 'react-hook-form'
import * as yup from 'yup'
import styles from './NewApplicationModal.module.scss'

const validationSchemaBirthdate = yup.object().shape({
  birthday: birthdayValidation.required(),
})

interface IBirthdayInputCheck {
  defaultBirthday?: string | null
  onSubmitBD: (a: any, b: any) => void
  result: UserSearch
  erroredSearchId: string | undefined
  inlineUserError: any
  retrievedUser: User | null | undefined
  retrievedUserIsUsed: boolean
  setCheckAndAdd: (arg: boolean) => void
}

export const BirthdayInputCheck: FC<IBirthdayInputCheck> = ({
  defaultBirthday,
  onSubmitBD,
  result,
  erroredSearchId,
  inlineUserError,
  retrievedUser,
  retrievedUserIsUsed,
  setCheckAndAdd,
}) => {
  const methodsBirthdate = useForm<{ birthday: string }>({
    resolver: yupResolver(validationSchemaBirthdate),
    defaultValues: {
      birthday: defaultBirthday || '',
    },
  })

  const { control: controlBirthdate, handleSubmit: handleSubmitBirthdate } =
    methodsBirthdate

  return (
    <form
      onSubmit={handleSubmitBirthdate(data =>
        onSubmitBD(data, {
          ...result,
          searchId: result._search_id,
        }),
      )}
    >
      <InlineSection>
        <Label required>Datum narození</Label>
        <FormInputError>
          <Controller
            control={controlBirthdate}
            name="birthday"
            render={({ field }) => <BirthdayInput {...field} />}
          />
        </FormInputError>
      </InlineSection>
      {erroredSearchId === result._search_id && (
        <ErrorBox
          // TODO: move this handling to errorbox
          error={
            (inlineUserError &&
              (inlineUserError as FetchBaseQueryError)
                .data) as ObjectWithStrings
          }
        />
      )}

      {!(
        retrievedUser &&
        retrievedUser._search_id === result._search_id &&
        retrievedUserIsUsed
      ) && (
        <Button
          className={styles.birthsdayButton}
          secondary
          type="submit"
          onClick={() => setCheckAndAdd(true)}
        >
          zkontroluj a přidej{' '}
        </Button>
      )}
      {retrievedUser &&
      retrievedUser._search_id === result._search_id &&
      retrievedUserIsUsed ? (
        <Button className={styles.birthsdayButton} secondary type="submit">
          přidej k účastníkům
        </Button>
      ) : (
        <Button className={styles.birthsdayButton} secondary type="submit">
          zkontroluj
        </Button>
      )}
    </form>
  )
}
