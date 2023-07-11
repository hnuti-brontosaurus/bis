import styles from './EmptyListPlaceholder.module.scss'

const images = [
  'https://i.ibb.co/QKTrnFq/lama.png',
  'https://i.ibb.co/HgkzpR2/tree-sun-green.png',
  'https://i.ibb.co/Rhks4G6/tree-sun.png',
  'https://i.ibb.co/m0GQt2K/kroliczek.png',
]

export const EmptyListPlaceholder = ({ label }: { label: string }) => {
  return (
    <div className={styles.emptyListWrapper}>
      <div className={styles.emptyListBox}>
        <img src={images[1]} alt="" width="200"></img>
        <div>{label}</div>
      </div>
    </div>
  )
}
