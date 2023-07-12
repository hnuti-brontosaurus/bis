import { useAppSelector } from 'app/hooks'
import { selectShowHeader } from 'features/ui/uiSlice'
import { ReactNode } from 'react'
import { Header } from './Header'
import { Content, Footer, Header as LayoutHeader, Layout } from './Layout'
import { LinkFooter } from './LinkFooter'

export const PageLayout = ({ children }: { children: ReactNode }) => {
  const showHeader = useAppSelector(selectShowHeader)
  return (
    <Layout page>
      {showHeader && (
        <LayoutHeader>
          <Header />
        </LayoutHeader>
      )}
      <Content>{children}</Content>
      {showHeader && (
        <Footer>
          <LinkFooter />
        </Footer>
      )}
    </Layout>
  )
}
