import { site } from '../content/site'
import { Logo } from './Logo'

export function Header() {
  return (
    <header className="fixed inset-x-0 top-0 z-40 bg-paper/80 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4 sm:px-8">
        <a href="#top">
          <Logo />
        </a>
        <nav className="hidden gap-6 text-sm lg:flex">
          {site.nav.map((item) => (
            <a key={item.id} href={`#${item.id}`} className="hover:text-accent">
              {item.label}
            </a>
          ))}
        </nav>
        <a href="#contacts" className="rounded-full bg-graphite px-5 py-2 text-sm text-stone hover:bg-graphite-soft">
          Забронировать
        </a>
      </div>
    </header>
  )
}
