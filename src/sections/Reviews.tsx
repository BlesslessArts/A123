import { Section } from '../components/Section'
import { site } from '../content/site'

export function Reviews() {
  return (
    <Section id="reviews" kicker="Отзывы" title="Что говорят гости">
      <div className="grid gap-6 md:grid-cols-3">
        {site.reviews.map((r, i) => (
          <figure key={i} className="rounded-2xl bg-navy p-8">
            <blockquote className="text-xl">«{r.text}»</blockquote>
            <figcaption className="mt-6 text-sm">
              {r.author}, <span className="opacity-70">{r.role}</span>
            </figcaption>
          </figure>
        ))}
      </div>
    </Section>
  )
}
