import { motion } from 'motion/react'
import { HERO_IMAGE, heroObjectPosition } from '../content/hero'
import { site } from '../content/site'

// TODO: фоновое видео с героем бренда, которое проигрывается при скролле
export function Hero({ ready }: { ready: boolean }) {
  const reveal = (delay: number) => ({
    initial: { opacity: 0, y: 24 },
    animate: ready ? { opacity: 1, y: 0 } : undefined,
    transition: { delay, duration: 0.8, ease: [0.2, 0.7, 0.2, 1] as const },
  })

  return (
    <section id="top" className="relative flex h-svh min-h-[560px] items-end overflow-hidden px-4 pb-16 sm:px-8 sm:pb-24">
      <img
        src={HERO_IMAGE.src}
        alt="Вид на Национальную библиотеку из арочного окна зала на закате"
        width={HERO_IMAGE.width}
        height={HERO_IMAGE.height}
        fetchPriority="high"
        className="absolute inset-0 h-full w-full object-cover"
        style={{ objectPosition: heroObjectPosition }}
      />
      <div className="absolute inset-0 bg-gradient-to-b from-night/70 via-night/10 to-night/90" />
      <div className="absolute inset-0 bg-gradient-to-r from-night/60 via-night/20 to-transparent" />
      <div className="relative mx-auto w-full max-w-6xl">
        <motion.h1 className="max-w-3xl text-5xl leading-[1.05] sm:text-7xl" {...reveal(0.1)}>
          {site.slogan}
        </motion.h1>
        <motion.p className="mt-6 max-w-xl text-lg text-plaster/85" {...reveal(0.25)}>
          123 м² с арочными окнами 4×3,5 м и видом на Национальную библиотеку — для мастер-классов, лекций и семинаров.
        </motion.p>
        <motion.ul className="mt-10 flex flex-wrap gap-x-10 gap-y-6" {...reveal(0.4)}>
          {site.facts.map((f) => (
            <li key={f.label}>
              <p className="text-4xl font-bold tracking-tight text-sunset">{f.value}</p>
              <p className="text-sm text-plaster/70">{f.label}</p>
            </li>
          ))}
        </motion.ul>
      </div>
    </section>
  )
}
