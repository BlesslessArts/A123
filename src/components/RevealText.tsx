import { motion } from 'motion/react'

// Заголовок выезжает из маски по словам (E2). Каждое слово сидит в overflow-hidden и поднимается снизу.
// play: true/false — запуск по сигналу (первый экран после прелоадера); не задан — при появлении на экране.

const EASE = [0.2, 0.75, 0.15, 1] as const

type Tag = 'h1' | 'h2' | 'h3'

export function RevealText({
  as = 'h2',
  text,
  className = '',
  delay = 0,
  play,
}: {
  as?: Tag
  text: string
  className?: string
  delay?: number
  play?: boolean
}) {
  const Heading = motion[as]
  const words = text.split(' ')
  const trigger =
    play === undefined
      ? { initial: 'hidden', whileInView: 'shown', viewport: { once: true, margin: '0px 0px -10% 0px' } }
      : { initial: 'hidden', animate: play ? 'shown' : 'hidden' }

  return (
    <Heading className={className} aria-label={text} {...trigger} transition={{ staggerChildren: 0.06, delayChildren: delay }}>
      {words.map((w, i) => (
        <span key={i} aria-hidden className="inline-block overflow-hidden pb-[0.12em] -mb-[0.12em] align-bottom">
          <motion.span
            className="inline-block"
            variants={{ hidden: { y: '110%' }, shown: { y: 0, transition: { duration: 0.9, ease: EASE } } }}
          >
            {w}
            {i < words.length - 1 && ' '}
          </motion.span>
        </span>
      ))}
    </Heading>
  )
}
