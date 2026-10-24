import { AnimatePresence, motion } from 'motion/react'
import { useEffect, useState } from 'react'

// Прелоадер: рисуем арку, затем проявляем название. Финальная идея анимации — после получения логотипа.
export function Preloader() {
  const [visible, setVisible] = useState(true)

  useEffect(() => {
    const done = () => setTimeout(() => setVisible(false), 600)
    if (document.readyState === 'complete') done()
    else window.addEventListener('load', done, { once: true })
    return () => window.removeEventListener('load', done)
  }, [])

  return (
    <AnimatePresence>
      {visible && (
        <motion.div
          className="fixed inset-0 z-50 grid place-items-center bg-graphite text-stone"
          exit={{ opacity: 0 }}
          transition={{ duration: 0.6 }}
        >
          <div className="flex flex-col items-center gap-4">
            <svg viewBox="0 0 64 64" className="h-20 w-20" aria-hidden>
              <motion.path
                d="M12 58V30a20 20 0 0 1 40 0v28"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                initial={{ pathLength: 0 }}
                animate={{ pathLength: 1 }}
                transition={{ duration: 1.2, ease: 'easeInOut' }}
              />
            </svg>
            <motion.span
              className="font-display text-2xl tracking-[0.3em]"
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.8 }}
            >
              АРКА 123
            </motion.span>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
