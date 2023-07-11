import {
  FormInputError,
  FormSection,
  FormSectionGroup,
  FormSubheader,
  FullSizeElement,
  htmlRequired,
  ImagesUpload,
  ImageUpload,
  RichTextEditor,
} from 'components'
import { form as formTexts } from 'config/static/event'
import { Controller, FormProvider } from 'react-hook-form'
import { required } from 'utils/validationMessages'
import { MethodsShapes } from '..'

export const InvitationStep = ({
  methods,
  isVolunteering,
}: {
  methods: MethodsShapes['invitation']
  isVolunteering: boolean
}) => {
  const { control } = methods

  return (
    <FormProvider {...methods}>
      <form>
        <FormSectionGroup startIndex={17}>
          <FormSection header="Pozvánka">
            <FullSizeElement>
              <FormSubheader
                required
                onWeb
                help={formTexts.propagation.invitation_text_introduction.help}
              >
                {formTexts.propagation.invitation_text_introduction.name}
              </FormSubheader>
              <FormInputError isBlock>
                <Controller
                  name="propagation.invitation_text_introduction"
                  control={control}
                  rules={{
                    required,
                    validate: {
                      required: htmlRequired(required),
                    },
                  }}
                  render={({ field }) => (
                    <RichTextEditor
                      placeholder={
                        formTexts.propagation.invitation_text_introduction.help
                      }
                      {...field}
                    />
                  )}
                />
              </FormInputError>
            </FullSizeElement>
            <FullSizeElement>
              <FormSubheader
                required
                onWeb
                help={
                  formTexts.propagation.invitation_text_practical_information
                    .help
                }
              >
                {
                  formTexts.propagation.invitation_text_practical_information
                    .name
                }
              </FormSubheader>
              <FormInputError isBlock>
                <Controller
                  name="propagation.invitation_text_practical_information"
                  control={control}
                  rules={{
                    required,
                    validate: {
                      required: htmlRequired(required),
                    },
                  }}
                  render={({ field }) => (
                    <RichTextEditor
                      placeholder={
                        formTexts.propagation
                          .invitation_text_practical_information.help
                      }
                      {...field}
                    />
                  )}
                />
              </FormInputError>
            </FullSizeElement>
            <FullSizeElement>
              <FormSubheader
                required={isVolunteering}
                onWeb
                help={
                  formTexts.propagation.invitation_text_work_description.help
                }
              >
                {formTexts.propagation.invitation_text_work_description.name}
              </FormSubheader>
              <FormInputError isBlock>
                <Controller
                  name="propagation.invitation_text_work_description"
                  control={control}
                  rules={{
                    required: isVolunteering && required,
                    validate: {
                      required: htmlRequired(isVolunteering && required),
                    },
                  }}
                  render={({ field }) => (
                    <RichTextEditor
                      placeholder={
                        formTexts.propagation.invitation_text_work_description
                          .help
                      }
                      {...field}
                    />
                  )}
                />
              </FormInputError>
            </FullSizeElement>
            <FullSizeElement>
              <FormSubheader
                onWeb
                help={formTexts.propagation.invitation_text_about_us.help}
              >
                {formTexts.propagation.invitation_text_about_us.name}
              </FormSubheader>
              <FormInputError isBlock>
                <Controller
                  name="propagation.invitation_text_about_us"
                  control={control}
                  rules={{}}
                  render={({ field }) => (
                    <RichTextEditor
                      placeholder={
                        formTexts.propagation.invitation_text_about_us.help
                      }
                      {...field}
                    />
                  )}
                />
              </FormInputError>
            </FullSizeElement>
          </FormSection>
          <FormSection
            header="Hlavní foto"
            required
            onWeb
            help="Hlavní foto se zobrazí v náhledu akce na webu"
          >
            <FormInputError>
              <ImageUpload required name="main_image.image" />
            </FormInputError>
          </FormSection>
          <FormSection
            header="Fotky k malé ochutnávce"
            onWeb
            help="Další fotky, které se zobrazí u akce."
          >
            <ImagesUpload name="images" />
          </FormSection>
        </FormSectionGroup>
      </form>
    </FormProvider>
  )
}
