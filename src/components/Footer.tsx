import { site } from '../content/site'
import { Logo } from './Logo'

const year = new Date().getFullYear()

export function Footer() {
  return (
    <footer id="contacts" className="bg-graphite px-4 py-16 text-stone sm:px-8">
      <div className="mx-auto grid max-w-6xl gap-10 sm:grid-cols-3">
        <div>
          <Logo />
          <p className="mt-4 font-display text-lg italic">{site.slogan}</p>
        </div>
        <div className="space-y-1 text-sm">
          <p>{site.address}</p>
          <p>{site.phone}</p>
          <p>{site.email}</p>
        </div>
        {/* TODO: форма заявки / ссылка на мессенджер */}
        <div className="text-sm opacity-70">© {year} {site.name}</div>
      </div>
    </footer>
  )
}
