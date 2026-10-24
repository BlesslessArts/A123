import { useEffect, useRef } from 'react'
import { ARCH, ARCH_STROKE, DIGITS, MARK_VIEWBOX, WORDMARK, WORDMARK_VIEWBOX } from './logo-paths'

// Знак-арка: на hover контур «обегает» арку, цифры подпрыгивают (H1). Анимации — в index.css (.logo-*).
export function LogoMark({ className = '' }: { className?: string }) {
  return (
    <svg viewBox={MARK_VIEWBOX} className={className} aria-hidden>
      <path className="logo-arch" d={ARCH} pathLength={1} fill="none" stroke="currentColor" strokeWidth={ARCH_STROKE} />
      {DIGITS.map((d, i) => (
        <path key={i} className="logo-digit" d={d} fill="currentColor" style={{ animationDelay: `${450 + i * 70}ms` }} />
      ))}
    </svg>
  )
}

export function Wordmark({ className = '' }: { className?: string }) {
  return (
    <svg viewBox={WORDMARK_VIEWBOX} className={className} aria-hidden>
      <path d={WORDMARK} fill="currentColor" fillRule="evenodd" />
    </svg>
  )
}

/** Знак + надпись. Анимация (H1) запускается при каждом наведении; play — проиграть один раз сама (после прелоадера). */
export function Logo({ className = '', play = false }: { className?: string; play?: boolean }) {
  const ref = useRef<HTMLSpanElement>(null)

  // Перезапуск CSS-анимации: снимаем класс, форсируем reflow, ставим снова
  const replay = () => {
    const el = ref.current
    if (!el) return
    el.classList.remove('logo-play')
    void el.offsetWidth
    el.classList.add('logo-play')
  }

  useEffect(() => {
    if (play) replay()
  }, [play])

  return (
    <span
      ref={ref}
      className={`logo inline-flex items-center gap-2.5 ${className}`}
      onPointerEnter={replay}
      onFocus={replay}
      onAnimationEnd={(e) => {
        // Снимаем класс, когда допрыгала последняя цифра
        if (e.animationName === 'logo-hop' && (e.target as Element).matches('.logo-digit:last-of-type'))
          e.currentTarget.classList.remove('logo-play')
      }}
    >
      <LogoMark className="h-9 w-auto" />
      <Wordmark className="h-4 w-auto" />
      <span className="sr-only">АРКА 123</span>
    </span>
  )
}
