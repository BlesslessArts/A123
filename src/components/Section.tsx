import type { ReactNode } from 'react'

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
    <section id={id} className={`px-4 py-24 sm:px-8 ${dark ? 'bg-graphite text-stone' : ''}`}>
      <div className="mx-auto max-w-6xl">
        {kicker && <p className="mb-3 text-xs uppercase tracking-[0.3em] text-accent">{kicker}</p>}
        <h2 className="mb-12 text-4xl sm:text-5xl">{title}</h2>
        {children}
      </div>
    </section>
  )
}
