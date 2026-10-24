import { site } from '../content/site'
import { Logo } from './Logo'

export function Header({ ready }: { ready: boolean }) {
  return (
    <header className="fixed inset-x-0 top-0 z-40 bg-night/60 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3 sm:px-8">
        <a href="#top" aria-label="АРКА 123, на главную">
          <Logo play={ready} />
        </a>
        <nav className="hidden gap-6 text-sm lg:flex">
          {site.nav.map((item) => (
            <a key={item.id} href={`#${item.id}`} className="text-plaster/80 hover:text-sunset">
              {item.label}
            </a>
          ))}
        </nav>
        <a href="#contacts" className="rounded-full bg-sunset px-5 py-2 text-sm font-semibold text-night hover:bg-plaster">
          Забронировать
        </a>
      </div>
    </header>
  )
}
