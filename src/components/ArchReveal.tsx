import { motion } from 'motion/react'
import type { ReactNode } from 'react'

// Фото раскрывается аркой (E3): маска стартует узкой аркой снизу и разворачивается в полный кадр,
// картинка внутри мягко отъезжает. Скругления в px, чтобы clip-path интерполировался плавно.

const EASE = [0.65, 0, 0.35, 1] as const
const FROM = 'inset(38% 16% 0% 16% round 400px 400px 0px 0px)'
const TO = 'inset(0% 0% 0% 0% round 12px 12px 12px 12px)'

export function ArchReveal({ children, delay = 0, className = '' }: { children: ReactNode; delay?: number; className?: string }) {
  return (
    <motion.div
      className={`overflow-hidden ${className}`}
      initial={{ clipPath: FROM }}
      whileInView={{ clipPath: TO }}
      viewport={{ once: true, margin: '0px 0px -12% 0px' }}
      transition={{ duration: 1.3, delay, ease: EASE }}
    >
      <motion.div
        initial={{ scale: 1.3 }}
        whileInView={{ scale: 1 }}
        viewport={{ once: true, margin: '0px 0px -12% 0px' }}
        transition={{ duration: 1.5, delay, ease: EASE }}
      >
        {children}
      </motion.div>
    </motion.div>
  )
}
