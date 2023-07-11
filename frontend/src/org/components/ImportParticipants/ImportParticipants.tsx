import { UserPayload } from 'app/services/bisTypes'
import spreadsheetTemplate from 'assets/templates/Vzor_import účastníků.xlsx'
import { ExternalButtonLink, ImportExcelButton, StyledModal } from 'components'
import { useShowMessage } from 'features/systemMessage/useSystemMessage'
import { useState } from 'react'
import { Overwrite } from 'utility-types'
import {
  ConfirmedUser,
  ImportParticipantsList,
} from './ImportParticipantsList/ImportParticipantsList'

export type UserImport = Overwrite<
  Omit<UserPayload, 'pronoun' | 'subscribed_to_newsletter' | 'all_emails'>,
  {
    health_insurance_company: string
    address: string
    contact_address: string
  }
>

export const ImportParticipants = ({
  onConfirm,
}: {
  onConfirm: (data: ConfirmedUser[]) => Promise<{
    create: UserPayload[]
    update: ({
      id: string
    } & Partial<UserPayload>)[]
  }>
}) => {
  const [importParticipantsModalOpen, setImportParticipantsModalOpen] =
    useState(false)

  const [importParticipantsData, setImportParticipantsData] =
    useState<UserImport[]>()

  const showMessage = useShowMessage()

  const handleConfirm = async (data: ConfirmedUser[]) => {
    try {
      const failedImports = await onConfirm(data)

      if (
        failedImports.create.length === 0 &&
        failedImports.update.length === 0
      ) {
        showMessage({
          message: 'Import se povedl',
          type: 'success',
        })
        setImportParticipantsModalOpen(false)
      }

      if (failedImports.create.length > 0) {
        showMessage({
          type: 'error',
          message: `Nepodařilo se nám vytvořit účastníky ${failedImports.create
            .map(({ first_name, last_name }) => `${first_name} ${last_name}`)
            .join(', ')}`,
        })
      }

      if (failedImports.update.length > 0) {
        showMessage({
          type: 'error',
          message: `Nepodařilo se nám upravit osobní informace účastníků ${failedImports.create
            .map(({ first_name, last_name }) => `${first_name} ${last_name}`)
            .join(', ')}`,
        })
      }
    } catch (e) {
      // just catch the error
    }
  }

  const handleCancel = () => {
    setImportParticipantsModalOpen(false)
    setImportParticipantsData(undefined)
  }

  const handleImportParticipants = async (data: UserImport[]) => {
    setImportParticipantsData(
      data.filter(
        ({ first_name, last_name, birthday }) =>
          first_name || last_name || birthday,
      ),
    )
    setImportParticipantsModalOpen(true)
  }

  return (
    <>
      <StyledModal
        title="Import účastnic a účastníků"
        open={importParticipantsModalOpen}
        onClose={handleCancel}
      >
        <ImportParticipantsList
          data={importParticipantsData}
          onConfirm={handleConfirm}
          onCancel={handleCancel}
        />
      </StyledModal>
      {/* Align template xlsx to center.
      Just being too lazy to make a separate stylesheet
      feel free to make one if you need to style more stuff :) */}
      <div style={{ textAlign: 'center' }}>
        <ImportExcelButton<UserImport>
          keyMap={{
            first_name: 0,
            last_name: 1,
            birthday: 2,
            email: 3,
            phone: 4,
            address: 5,
            contact_address: 6,
            health_insurance_company: 7,
            health_issues: 8,
            close_person: {
              first_name: 9,
              last_name: 10,
              email: 11,
              phone: 12,
            },
            birth_name: 13,
            nickname: 14,
          }}
          headerRows={2}
          onUpload={handleImportParticipants}
        >
          Importovat z excelu
        </ImportExcelButton>{' '}
        <ExternalButtonLink tertiary small href={spreadsheetTemplate}>
          (vzor .xlsx)
        </ExternalButtonLink>
      </div>
    </>
  )
}
