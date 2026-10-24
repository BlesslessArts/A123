import { motion, useScroll, useTransform } from 'motion/react'
import { useRef } from 'react'
import { RevealText } from '../components/RevealText'
import { HERO_IMAGE, heroObjectPosition } from '../content/hero'
import { site } from '../content/site'

// Параллакс (E1): при прокрутке фото уходит медленнее и приближается к окну, текст уезжает быстрее и гаснет.
// При progress = 0 трансформаций нет — кадр совпадает с последним кадром прелоадера.
// TODO: фоновое видео с героем бренда, которое проигрывается при скролле
export function Hero({ ready }: { ready: boolean }) {
  const ref = useRef<HTMLElement>(null)
  const { scrollYProgress } = useScroll({ target: ref, offset: ['start start', 'end start'] })
  const imageY = useTransform(scrollYProgress, [0, 1], ['0%', '6%'])
  const imageScale = useTransform(scrollYProgress, [0, 1], [1, 1.2])
  const textY = useTransform(scrollYProgress, [0, 1], ['0%', '-40%'])
  const textOpacity = useTransform(scrollYProgress, [0, 0.6], [1, 0])

  return (
    <section
      ref={ref}
      id="top"
      className="relative flex h-svh min-h-[560px] items-end overflow-hidden px-4 pb-16 sm:px-8 sm:pb-24"
    >
      <motion.img
        src={HERO_IMAGE.src}
        alt="Вид на Национальную библиотеку из арочного окна зала на закате"
        width={HERO_IMAGE.width}
        height={HERO_IMAGE.height}
        fetchPriority="high"
        className="absolute inset-0 h-full w-full object-cover"
        style={{ objectPosition: heroObjectPosition, transformOrigin: heroObjectPosition, y: imageY, scale: imageScale }}
      />
      <div className="absolute inset-0 bg-gradient-to-b from-night/70 via-night/10 to-night/90" />
      <div className="absolute inset-0 bg-gradient-to-r from-night/60 via-night/20 to-transparent" />
      <motion.div className="relative mx-auto w-full max-w-6xl" style={{ y: textY, opacity: textOpacity }}>
        <RevealText as="h1" text={site.slogan} play={ready} delay={0.1} className="max-w-3xl text-5xl leading-[1.05] sm:text-7xl" />
        <motion.p
          className="mt-6 max-w-xl text-lg text-plaster/85"
          initial={{ opacity: 0, y: 16 }}
          animate={ready ? { opacity: 1, y: 0 } : undefined}
          transition={{ delay: 0.6, duration: 0.8, ease: [0.2, 0.7, 0.2, 1] }}
        >
          123 м² с арочными окнами 4×3,5 м и видом на Национальную библиотеку — для мастер-классов, лекций и семинаров.
        </motion.p>
      </motion.div>
    </section>
  )
}
