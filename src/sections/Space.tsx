import { useState } from 'react'
import { Section } from '../components/Section'
import { site } from '../content/site'

// TODO: 3D/360° демо помещения (three.js или панорама) с переключением вариантов рассадки
export function Space() {
  const [layout, setLayout] = useState<string>(site.layouts[0].id)

  return (
    <Section id="space" kicker="Помещение" title="123 м² света" dark>
      <div className="mb-6 flex flex-wrap gap-2">
        {site.layouts.map((l) => (
          <button
            key={l.id}
            onClick={() => setLayout(l.id)}
            className={`rounded-full border px-4 py-2 text-sm ${
              layout === l.id ? 'border-stone bg-stone text-graphite' : 'border-stone/40 hover:border-stone'
            }`}
          >
            {l.label}
          </button>
        ))}
      </div>
      <div className="grid aspect-video place-items-center rounded-2xl bg-graphite-soft text-stone/60">
        3D-демо: {site.layouts.find((l) => l.id === layout)?.label}
      </div>
    </Section>
  )
}
