import React, { forwardRef, Suspense } from 'react'
import { ControllerRenderProps } from 'react-hook-form'
import 'react-quill/dist/quill.core.css'
import 'react-quill/dist/quill.snow.css'
import { stripHtml } from 'utils/helpers'
import styles from './RichTextEditor.module.scss'
const ReactQuill = React.lazy(() => import('react-quill'))

const config = {
  toolbar: ['bold', { list: 'ordered' }, { list: 'bullet' }, 'link'],
  keyboard: {
    bindings: {
      tab: {
        key: 9,
        handler: function () {
          return true
        },
      },
    },
  },
}

export const RichTextEditor = forwardRef<
  any,
  ControllerRenderProps<any, string> & { placeholder?: string }
>((props, ref) => (
  <Suspense>
    <ReactQuill
      className={styles.wrapper}
      theme="snow"
      modules={config}
      formats={['bold', 'list', 'bullet', 'link']}
      {...props}
      id={props.name}
      ref={ref}
    />
  </Suspense>
))

// TODO rewrite to yay schema
export const htmlRequired =
  (required: string | boolean) =>
  (value: string = '') =>
    !required || stripHtml(value).trim().length > 0 || required
