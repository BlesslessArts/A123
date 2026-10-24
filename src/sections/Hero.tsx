import { motion } from 'motion/react'
import { site } from '../content/site'

// TODO: фоновое видео с героем бренда, которое проигрывается при скролле
export function Hero() {
  return (
    <section id="top" className="relative flex min-h-screen items-end bg-graphite px-4 pb-24 pt-32 text-stone sm:px-8">
      <div className="mx-auto w-full max-w-6xl">
        <motion.h1
          className="max-w-3xl text-5xl leading-tight sm:text-7xl"
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.6, duration: 0.8 }}
        >
          {site.slogan}
        </motion.h1>
        <p className="mt-6 max-w-xl text-lg opacity-80">
          123 м² с арочными окнами 4×3,5 м и видом на Национальную библиотеку — для мастер-классов, лекций и семинаров.
        </p>
        <ul className="mt-12 flex flex-wrap gap-10">
          {site.facts.map((f) => (
            <li key={f.label}>
              <p className="font-display text-4xl">{f.value}</p>
              <p className="text-sm opacity-70">{f.label}</p>
            </li>
          ))}
        </ul>
      </div>
    </section>
  )
}
