import { animate, motion, useMotionValue, useMotionValueEvent } from 'motion/react'
import { useEffect, useLayoutEffect, useRef, useState } from 'react'
import { HERO_IMAGE, coverRect } from '../content/hero'
import { ARCH, ARCH_HOLE, ARCH_STROKE, DIGITS, MARK_CENTER, MARK_HEIGHT } from './logo-paths'

// Прелоадер L2 «Окно открывается»: арка рисуется, в ней появляется вид на Библиотеку,
// и арка распахивается на весь экран, превращаясь в первый экран сайта (тот же кадр, что в Hero).
// Показывается один раз за сессию; при prefers-reduced-motion не показывается.

const SEEN_KEY = 'arka-intro-seen'
const MIN_MS = 1400
const MAX_WAIT_MS = 3000

function shouldShow() {
  try {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return false
    return sessionStorage.getItem(SEEN_KEY) !== '1'
  } catch {
    return true
  }
}

/** Шрифт и фото героя готовы — но не дольше MAX_WAIT_MS */
function assetsReady() {
  const img = new Image()
  img.src = HERO_IMAGE.src
  const ready = Promise.all([document.fonts.ready, img.decode().catch(() => undefined)])
  return Promise.race([ready, new Promise((r) => setTimeout(r, MAX_WAIT_MS))])
}

/** Масштаб, при котором «окно» арки целиком закрывает экран w×h */
function coverScale(w: number, h: number) {
  const cy = MARK_CENTER.y
  const r = 284.5
  const arcY = 597
  for (let s = 0.2; s < 60; s *= 1.02) {
    const halfW = w / 2 / s
    const halfH = h / 2 / s
    const sidesOk = halfW <= r && cy + halfH <= 974.5
    const topY = cy - halfH
    const topOk = topY >= arcY || Math.hypot(halfW, arcY - topY) <= r
    if (sidesOk && topOk) return s * 1.04
  }
  return 60
}

export function Preloader({ onDone }: { onDone: () => void }) {
  const [visible, setVisible] = useState(shouldShow)
  const [size, setSize] = useState({ w: window.innerWidth, h: window.innerHeight })
  const holeRef = useRef<SVGPathElement>(null)
  const markRef = useRef<SVGGElement>(null)

  const startScale = Math.min(size.h * 0.34, 280) / MARK_HEIGHT
  const scale = useMotionValue(startScale)
  const draw = useMotionValue(0)
  const digits = useMotionValue(0)
  const photo = useMotionValue(0)
  const mark = useMotionValue(1)
  const overlay = useMotionValue(1)

  const transformAt = (s: number) =>
    `translate(${size.w / 2} ${size.h / 2}) scale(${s}) translate(${-MARK_CENTER.x} ${-MARK_CENTER.y})`

  const applyScale = (s: number) => {
    holeRef.current?.setAttribute('transform', transformAt(s))
    markRef.current?.setAttribute('transform', transformAt(s))
  }
  useMotionValueEvent(scale, 'change', applyScale)
  useLayoutEffect(() => applyScale(scale.get()))

  useEffect(() => {
    if (!visible) {
      onDone()
      return
    }
    const onResize = () => setSize({ w: window.innerWidth, h: window.innerHeight })
    window.addEventListener('resize', onResize)
    document.documentElement.style.overflow = 'hidden'

    let cancelled = false
    const run = async () => {
      const started = performance.now()
      const ready = assetsReady()
      await new Promise((r) => setTimeout(r, 200))
      animate(draw, 1, { duration: 0.9, ease: 'easeInOut' })
      await new Promise((r) => setTimeout(r, 500))
      await animate(digits, 1, { duration: 0.45 })
      await ready
      const left = MIN_MS - (performance.now() - started)
      if (left > 0) await new Promise((r) => setTimeout(r, left))
      if (cancelled) return
      await animate(photo, 1, { duration: 0.6 })
      await animate(digits, 0, { duration: 0.3 })
      const end = coverScale(window.innerWidth, window.innerHeight)
      animate(mark, 0, { duration: 0.6, delay: 0.6 })
      await animate(scale, end, { duration: 1.2, ease: [0.7, 0, 0.2, 1] })
      onDone()
      await animate(overlay, 0, { duration: 0.45 })
      if (cancelled) return
      try {
        sessionStorage.setItem(SEEN_KEY, '1')
      } catch {
        /* приватный режим — просто покажем ещё раз */
      }
      setVisible(false)
    }
    run()

    return () => {
      cancelled = true
      window.removeEventListener('resize', onResize)
      document.documentElement.style.overflow = ''
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [visible])

  if (!visible) return null

  const img = coverRect(size.w, size.h)

  return (
    <motion.div className="fixed inset-0 z-50 bg-navy" style={{ opacity: overlay }} aria-hidden>
      <svg className="h-full w-full" viewBox={`0 0 ${size.w} ${size.h}`}>
        <defs>
          <clipPath id="preloader-window">
            <path ref={holeRef} d={ARCH_HOLE} />
          </clipPath>
        </defs>
        <motion.image
          href={HERO_IMAGE.src}
          x={img.x}
          y={img.y}
          width={img.width}
          height={img.height}
          preserveAspectRatio="none"
          clipPath="url(#preloader-window)"
          style={{ opacity: photo }}
        />
        <motion.g ref={markRef} className="text-plaster" style={{ opacity: mark }}>
          <motion.path
            d={ARCH}
            fill="none"
            stroke="currentColor"
            strokeWidth={ARCH_STROKE}
            style={{ pathLength: draw }}
          />
          <motion.g style={{ opacity: digits }}>
            {DIGITS.map((d, i) => (
              <path key={i} d={d} fill="currentColor" />
            ))}
          </motion.g>
        </motion.g>
      </svg>
    </motion.div>
  )
}
