import type { ReactNode } from 'react'
import { RevealText } from './RevealText'

export function Section({
  id,
  title,
  kicker,
  dark = false,
  children,
}: {
  id: string
  title: string
  kicker?: string
  dark?: boolean
  children: ReactNode
}) {
  return (
    <section id={id} className={`px-4 py-24 sm:px-8 ${dark ? 'bg-navy' : ''}`}>
      <div className="mx-auto max-w-6xl">
        {kicker && <p className="mb-3 text-xs uppercase tracking-[0.3em] text-sunset">{kicker}</p>}
        <RevealText text={title} className="mb-12 text-4xl sm:text-5xl" />
        {children}
      </div>
    </section>
  )
}
