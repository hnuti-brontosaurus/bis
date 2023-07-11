import { useAppDispatch, useAppSelector } from 'app/hooks'
import { ReactComponent as HiddenOwl } from 'assets/hiddenOwl.svg'
import { ReactComponent as Owl } from 'assets/owl.svg'
import classNames from 'classnames'
import { SpeechBubble } from 'components/SpeechBubble/SpeechBubble'
import { actions, selectInfoMessageVisibility } from 'features/ui/uiSlice'
import { ReactNode, useCallback, useEffect, useState } from 'react'
import { IoMdCloseCircle } from 'react-icons/io'
import styles from './GuideOwl.module.scss'

interface GuideOwlProps {
  children: ReactNode
  id: string
  left?: boolean
}

/*
Hey there fellow programmer, welcome to the GuideOwl component!
This little guy is here to help guide users through their journey on the website.
Just click on the hidden owl icon and he'll pop up with some helpful tips and tricks.
You can put him on the right or on the left.
But be careful, if you're thinking about changing the owl icon to a brontosaurus icon,
let me tell you, the consequences will be dire. Kittens everywhere will be disgusted and may even perish.
So please, for the sake of the kittens, keep the owl icon as is.
Thanks for understanding, and happy coding!
*/
export const GuideOwl = ({ children, id, left }: GuideOwlProps) => {
  const [animating, setAnimating] = useState(false)
  const [animatingOwl, setAnimatingOwl] = useState(false)

  const show = useAppSelector(state => selectInfoMessageVisibility(state, id))

  const dispatch = useAppDispatch()
  const setShow = useCallback(
    (show: boolean) => dispatch(actions.toggleInfoMessage({ show, id })),
    [dispatch, id],
  )

  // This effect is used to delay the appearance of the speech bubble after the owl animation is complete,
  // that gives an owl a liitle time to bounce
  useEffect(() => {
    if (!animating) {
      return
    }
    const timeout = setTimeout(() => {
      setAnimating(false)
      setShow(true)
    }, 800)

    return () => clearTimeout(timeout)
  }, [animating, setShow])

  // This effect is used to delay the appearance of the speech bubble after the owl animation is complete,
  // so it starts after the buncing owl animation is finished
  useEffect(() => {
    if (!animatingOwl && !animating) {
      return
    }
    const timeout = setTimeout(() => {
      setAnimatingOwl(false)
    }, 1800)

    return () => clearTimeout(timeout)
  }, [animatingOwl, animating])
  return (
    <>
      <div
        className={classNames(
          styles.guideOwl,
          styles.desktopContainer,
          left && styles.left,
        )}
      >
        {show ? (
          <>
            {/*
            And here we have the trusty SpeechBubble component,
            helping our little owl friend convey all his wise words.
            It's fully customizable, so feel free to add your own personal touch.
            */}
            <SpeechBubble
              className={classNames(
                styles.bubble,
                animatingOwl ? styles.animatingOwl : '',
              )}
              id={styles.desktopBubbleOwlGuide}
              left={left}
            >
              {children}
            </SpeechBubble>
            {/*huuu huuuuuuu! We already have a majestic brontosaurus in our logo,
            so don't add another one ;(((((
            But feel free to spread your wings and explore other extinct animals
            like unicorns, dodos, and phoenixes for your guide icon.
            Just remember, one dino is enough for us. Keep it wild and fun!
            #brontosaurusIsOnlyOne #BringBackTheExtinct #IWokeUpLikeThis*/}
            <Owl
              className={classNames(
                styles.owl,
                animatingOwl ? styles.animatingOwl : '',
              )}
              id={styles.owlGuideIcon}
            />
            {/* ↑↑↑↑↑↑↑↑↑
              Using the second brontosaurus in this design would detract from the overall aesthetic and disrupt the visual harmony.
              So, please, don't change the icon to brontosaurus. - Talita 
             */}
            <div
              className={classNames(
                styles.close,
                animatingOwl ? styles.animatingOwl : '',
              )}
              id="closeOwlGuide"
              onClick={() => setShow(false)}
            >
              <IoMdCloseCircle size={24} />
            </div>
          </>
        ) : (
          <div
            className={classNames(
              styles.hiddenOwlContainer,
              !show ? styles.hidden : '',
              animating ? styles.animating : '',
              left && styles.left,
            )}
            onClick={() => {
              setAnimating(true)
              setAnimatingOwl(true)
            }}
          >
            <HiddenOwl className={styles.hiddenOwl} />
          </div>
        )}
      </div>
      <div className={styles.mobileContainer}>
        {show ? (
          <>
            <SpeechBubble className={styles.mobileBubble} hideTail>
              {children}{' '}
              <div
                className={styles.mobileBubbleClose}
                onClick={() => setShow(false)}
              >
                <IoMdCloseCircle size={24} />
              </div>
            </SpeechBubble>
          </>
        ) : (
          <div
            className={classNames(
              styles.hiddenOwlContainer,
              !show ? styles.hidden : '',
              animating ? styles.animating : '',
            )}
            onClick={() => {
              setAnimating(true)
              setAnimatingOwl(true)
            }}
          >
            <HiddenOwl className={styles.hiddenOwl} />
          </div>
        )}
      </div>
    </>
  )
}
