import { FormInputError } from 'components'
import { FC, useEffect } from 'react'
import { FormProvider, useForm } from 'react-hook-form'
import { FaAngleLeft, FaAngleRight } from 'react-icons/fa'
import styles from './Pagination.module.scss'

export const Pagination: FC<{
  page: number
  pages: number
  onPageChange: (next: number) => void
}> = ({ page, pages, onPageChange }) => {
  const methods = useForm<{
    page: number
  }>()

  const { register, handleSubmit, reset } = methods

  const handleFormSubmit = handleSubmit(({ page }) => {
    onPageChange(page)
    reset()
  })

  // if page is invalid, change it to the nearest valid value
  useEffect(() => {
    if (page !== Math.floor(page)) onPageChange(Math.floor(page))
    if (page < 1) onPageChange(1)
    if (page > pages) onPageChange(pages)
  }, [onPageChange, page, pages])

  if (pages <= 1) return null

  return (
    <div className={styles.container}>
      <nav className={styles.pages}>
        {/* Previous page */}
        <button disabled={page < 2} onClick={() => onPageChange(page - 1)}>
          <FaAngleLeft size={30} />
        </button>
        {/* First page */}
        {page > 1 && <button onClick={() => onPageChange(1)}>1</button>}
        {/* Separator */}
        {page > 2 && <span>&hellip;</span>}
        {/* Current page */}
        <button className={styles.active} onClick={() => onPageChange(page)}>
          {page}
        </button>
        {/* Separator */}
        {page < pages - 1 && <span>&hellip;</span>}
        {/* Last Page */}
        {page < pages && (
          <button onClick={() => onPageChange(pages)}>{pages}</button>
        )}
        {/* Next page */}
        <button
          disabled={page > pages - 1}
          onClick={() => onPageChange(page + 1)}
        >
          <FaAngleRight size={30} />
        </button>
      </nav>
      <FormProvider {...methods}>
        <form onSubmit={handleFormSubmit} className={styles.exact}>
          Přejdi na stranu{' '}
          <FormInputError>
            <input
              type="number"
              size={2}
              {...register('page', {
                required: true,
                min: 1,
                max: pages,
              })}
            />
          </FormInputError>
          <input type="submit" value="Jdi" />
        </form>
      </FormProvider>
    </div>
  )
}
