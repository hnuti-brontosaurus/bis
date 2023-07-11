import { footerLinks, footerText } from 'config/static/footer'
import styles from './LinkFooter.module.scss'

export const LinkFooter = () => {
  return (
    <div className={styles.container}>
      <p>{footerText}</p>
      <nav className={styles.links}>
        {footerLinks.map(({ name, url }) => (
          <a
            key={name + url}
            href={url}
            target="_blank"
            rel="noopener noreferrer"
          >
            {name}
          </a>
        ))}
      </nav>
    </div>
  )
}
