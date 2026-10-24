import { Section } from '../components/Section'
import { site } from '../content/site'

export function Services() {
  return (
    <Section id="services" kicker="Услуги и цены" title="Для чего подходит зал">
      <div className="grid gap-6 sm:grid-cols-2">
        {site.services.map((s) => (
          <article key={s.title} className="rounded-2xl border border-plaster/10 p-8">
            <h3 className="text-2xl">{s.title}</h3>
            <p className="mt-3 opacity-80">{s.text}</p>
            <p className="mt-6 text-sm text-sunset">{s.price}</p>
          </article>
        ))}
      </div>
    </Section>
  )
}
