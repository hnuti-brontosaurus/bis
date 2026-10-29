import { FC } from 'react'
import { AddImageButton } from './AddImageButton'

interface Props {
  name: string // necessary for testing purposes (e2e tester needs to find the input)
  onAdd: (files: FileList) => void
  colorTheme?: string
}

export const AddImageInput: FC<Props> = ({ name, onAdd, colorTheme }) => (
  <label tabIndex={0}>
    <input
      name={name}
      style={{ display: 'none' }}
      type="file"
      accept="image/*,application/pdf"
      multiple
      onChange={event => event.target.files && onAdd(event.target.files)}
    />
    <AddImageButton colorTheme={colorTheme}>Přidej fotky</AddImageButton>
  </label>
)
