import { animate, useInView } from 'motion/react'
import { useEffect, useRef } from 'react'
import { site } from '../content/site'

// Цифры досчитываются при появлении и бегущая строка с форматами событий (E7). Стоит между первым экраном и «О нас».

type Stat = (typeof site.stats)[number]

function format(s: Stat, v: number) {
  const dec = 'decimals' in s ? s.decimals : 0
  return `${'prefix' in s ? s.prefix : ''}${v.toFixed(dec).replace('.', ',')}${'suffix' in s ? s.suffix : ''}`
}

function Counter({ stat, delay }: { stat: Stat; delay: number }) {
  const ref = useRef<HTMLParagraphElement>(null)
  const inView = useInView(ref, { once: true, margin: '0px 0px -15% 0px' })

  useEffect(() => {
    const el = ref.current
    if (!el || !inView) return
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      el.textContent = format(stat, stat.value)
      return
    }
    const controls = animate(0, stat.value, {
      duration: 1.8,
      delay,
      ease: [0.16, 1, 0.3, 1],
      onUpdate: (v) => (el.textContent = format(stat, v)),
    })
    return () => controls.stop()
  }, [inView, stat, delay])

  return (
    <p ref={ref} className="whitespace-nowrap text-4xl font-bold tracking-tight text-sunset tabular-nums sm:text-5xl">
      {format(stat, 0)}
    </p>
  )
}

export function Stats() {
  return (
    <section aria-label="Зал в цифрах" className="border-b border-plaster/10">
      <div className="mx-auto grid max-w-6xl grid-cols-2 gap-x-6 gap-y-10 px-4 py-16 sm:px-8 md:grid-cols-4">
        {site.stats.map((s, i) => (
          <div key={s.label}>
            <Counter stat={s} delay={i * 0.12} />
            <p className="mt-2 text-sm text-plaster/70">{s.label}</p>
          </div>
        ))}
      </div>
      <div className="overflow-hidden border-t border-plaster/10 py-5" aria-hidden>
        <div className="marquee flex w-max text-xl font-semibold sm:text-2xl">
          {[0, 1].map((k) => (
            <span key={k} className="whitespace-nowrap">
              {site.formats.map((w) => (
                <span key={w}>
                  {w}
                  <span className="px-6 text-sunset">·</span>
                </span>
              ))}
            </span>
          ))}
        </div>
      </div>
    </section>
  )
}
