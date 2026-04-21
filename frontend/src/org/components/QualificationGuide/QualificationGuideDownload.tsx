import { ReactNode } from 'react'
import styles from './QualificationGuide.module.scss'

export const QualificationGuideDownload = ({
  children,
}: {
  children: ReactNode
}) => {
  return (
    <a
      className={styles.link}
      target="_blank"
      rel="noopener noreferrer"
      href="https://drive.google.com/file/d/1kA-Kyipm4BF6bgeoO98MZTXjCaFQ-Ril/view?usp=sharing"
    >
      {children}
    </a>
  )
}

// export default to be able to lazy load
// eslint-disable-next-line import/no-default-export
export default QualificationGuideDownload
