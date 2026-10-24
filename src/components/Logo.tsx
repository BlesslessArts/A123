import { ARCH, ARCH_STROKE, DIGITS, MARK_VIEWBOX, WORDMARK, WORDMARK_VIEWBOX } from './logo-paths'

// Знак-арка: на hover контур «обегает» арку, цифры подпрыгивают (H1). Анимации — в index.css (.logo-*).
export function LogoMark({ className = '' }: { className?: string }) {
  return (
    <svg viewBox={MARK_VIEWBOX} className={className} aria-hidden>
      <path className="logo-arch" d={ARCH} pathLength={1} fill="none" stroke="currentColor" strokeWidth={ARCH_STROKE} />
      {DIGITS.map((d, i) => (
        <path key={i} className="logo-digit" d={d} fill="currentColor" style={{ transitionDelay: `${550 + i * 70}ms` }} />
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

/** Знак + надпись. play — проиграть hover-анимацию один раз (для тач-устройств после прелоадера). */
export function Logo({ className = '', play = false }: { className?: string; play?: boolean }) {
  return (
    <span className={`logo inline-flex items-center gap-2.5 ${play ? 'logo-play' : ''} ${className}`}>
      <LogoMark className="h-9 w-auto" />
      <Wordmark className="h-4 w-auto" />
      <span className="sr-only">АРКА 123</span>
    </span>
  )
}
