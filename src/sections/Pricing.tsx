import { Section } from '../components/Section'
import { site } from '../content/site'

export function Pricing() {
  return (
    <Section id="pricing" kicker="Тарифы" title="Сколько стоит" dark>
      <div className="grid gap-6 md:grid-cols-3">
        {site.plans.map((p) => (
          <article
            key={p.title}
            className={`rounded-2xl p-8 ${'featured' in p && p.featured ? 'bg-stone text-graphite' : 'border border-stone/20'}`}
          >
            <h3 className="text-2xl">{p.title}</h3>
            <p className="mt-4 font-display text-4xl">{p.price}</p>
            <ul className="mt-6 space-y-2 text-sm">
              {p.features.map((f) => (
                <li key={f}>— {f}</li>
              ))}
            </ul>
          </article>
        ))}
      </div>
    </Section>
  )
}
