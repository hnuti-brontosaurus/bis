import { CellConfig, jsPDF } from 'jspdf'
import { formatDateRange, formatDateTime } from 'utils/helpers'
// import { Person } from '../../person/types'
// import { NullableEventProps } from '../types'
import { Roboto, RobotoBlack } from './fonts'
import { conditions, conditionsTitle, safety, safetyTitle } from './text'

const BLANK_CELLS_FOR_PARTICIPANTS = 50

export const generatePdf = (participants: any, event: any) => {
  const doc = new jsPDF({ putOnlyUsedFonts: true, orientation: 'landscape' })

  const { name = '', start = '', end = '', location = '' } = event

  /** For using UTF-8 in generated pdf it is necessary
   *  to import a font that supports UTF-8 encoding
   *
   * To add a new font you can follow the following steps that we used here
   * or find info here: https://github.com/parallax/jsPDF#use-of-unicode-characters--utf-8
   * 1. const myFont = ... // load the *.ttf font file as binary string (file fonts.ts)
   * 2. doc.addFileToVFS("MyFont.ttf", myFont);
   * 3. doc.addFont("MyFont.ttf", "MyFont", "normal");
   * doc.setFont("MyFont");
   *  */
  doc.addFileToVFS('Roboto.ttf', Roboto)
  doc.addFont('Roboto.ttf', 'Roboto', 'normal')
  doc.addFileToVFS('RobotoBlack.ttf', RobotoBlack)
  doc.addFont('RobotoBlack.ttf', 'RobotoBlack', 'normal')

  /** Title */
  doc.setFont('RobotoBlack')
  doc.setFontSize(24)
  doc.text('Prezenční listina ', 50, 15)

  /** Left Data */
  doc.setFont('RobotoBlack')
  doc.setFontSize(14)
  doc.text('Akce: ', 20, 30)
  doc.setFont('Roboto')
  doc.text(`${name || ''}`, 40, 30)
  /** TODO: Get location in readable form */
  doc.setFont('RobotoBlack')
  doc.text('Místo: ', 20, 38)
  doc.setFont('Roboto')
  doc.text(`${location && location.name ? location.name : ' '}`, 42, 38)
  doc.setFont('RobotoBlack')
  const dates = formatDateRange(start, end)
  doc.text('Datum: ', 20, 46)
  doc.setFont('Roboto')
  doc.text(dates, 40, 46)
  /** Logo */
  doc.addImage(
    'https://i.ibb.co/GQVswbN/logo-44ee59a67744e7267959.png',
    'JPEG',
    170,
    10,
    110,
    28,
  )

  /** Right Data */
  doc.setFont('RobotoBlack')
  doc.text('ZČ/RC/Klub HB: ', 150, 46)
  doc.setFont('Roboto')
  doc.text(`${event.administration_units_names.join(', ')}`, 190, 46)

  /** GDPR */

  doc.setFontSize(10)
  doc.setFont('RobotoBlack')
  doc.text(conditionsTitle, 20, 54)
  doc.setFont('Roboto')

  const conditionsPrint = doc.splitTextToSize(conditions, 250)
  doc.text(conditionsPrint, 20, 60)
  doc.setFont('RobotoBlack')
  doc.text(safetyTitle, 20, 108)
  doc.setFont('Roboto')
  const safetyToPrint = doc.splitTextToSize(safety, 250)
  doc.text(safetyToPrint, 20, 113)
  //   doc.setFont('RobotoBlack')
  //   doc.text(declarationTitle, 20, 122)
  //   doc.setFont('Roboto')
  //   doc.text(declaration, 40, 122)
  /** Table */
  doc.setFont('Roboto')

  function removePrefixFromPhone(phone: string): string {
    const prefix = '+420'
    if (phone.startsWith(prefix)) {
      return phone.slice(prefix.length)
    }
    return phone
  }
  const participantsToPrint = participants.map(
    (
      { first_name, last_name, birthday, phone, email, address }: any,
      index: any,
    ) => ({
      id: `${index + 1}.`,
      first_name,
      last_name,
      birthday: birthday ? formatDateTime(birthday) : ' ',
      address:
        (address?.street ? address.street : ' ') +
        (address?.city ? address.city : ''),
      postalCode: address?.zip_code ? address.zip_code : ' ',
      phone: phone ? removePrefixFromPhone(phone) : ' ',
      email: email || ' ',
      signature: ' ',
    }),
  )
  let index = participants.length
  const maxIndex = index + BLANK_CELLS_FOR_PARTICIPANTS
  while (index < maxIndex) {
    participantsToPrint.push({
      id: `${index + 1}.`,
      first_name: ' ',
      last_name: ' ',
      birthday: ' ',
      address: ' ',
      postalCode: ' ',
      signature: ' ',
      phone: ' ',
      email: ' ',
    })
    index += 1
  }
  const headers: CellConfig[] = [
    {
      name: 'id',
      prompt: ' ',
      width: 15,
      align: 'center',
      padding: 0,
    },
    {
      name: 'first_name',
      prompt: 'Jméno',
      width: 35,
      align: 'center',
      padding: 0,
    },
    {
      name: 'last_name',
      prompt: 'Príjmení',
      width: 45,
      align: 'center',
      padding: 0,
    },
    {
      name: 'birthday',
      prompt: 'Datum narození',
      width: 50,
      align: 'center',
      padding: 0,
    },
    {
      name: 'address',
      prompt: 'Bydlište',
      width: 47,
      align: 'center',
      padding: 0,
    },
    {
      name: 'postalCode',
      prompt: 'PSC',
      width: 20,
      align: 'center',
      padding: 0,
    },
    {
      name: 'phone',
      prompt: 'Telefon',
      width: 40,
      align: 'center',
      padding: 0,
    },
    {
      name: 'email',
      prompt: 'E-mail',
      width: 65,
      align: 'center',
      padding: 0,
    },
    {
      name: 'signature',
      prompt: 'Podpis',
      width: 29,
      align: 'center',
      padding: 20,
    },
  ]
  // margins arount the table
  const margins = {
    top: 10,
    bottom: 10,
    left: 0,
    width: 1000,
  }

  const config = {
    padding: 1,
    // this seems necessary to set font properties in the table
    margins,
    rowStart: () => {
      doc.setFont('Roboto')
      doc.setFontSize(10)
    },
    printHeaders: true,
    headerBackgroundColor: '#fff',
    fontSize: 10,
  }
  /** TODO:  
    remove those comments
    when this PR is accepted: https://github.com/parallax/jsPDF/pull/3351
    so probably never
  */
  // eslint-disable-next-line @typescript-eslint/ban-ts-comment
  // @ts-ignore
  doc.table(20, 125, participantsToPrint, headers, config)
  return doc
}
