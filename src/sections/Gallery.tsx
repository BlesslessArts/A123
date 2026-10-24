import { Section } from '../components/Section'

// TODO: обработанные фото (без следов ремонта) положить в public/media/gallery
const placeholders = Array.from({ length: 6 }, (_, i) => i)

export function Gallery() {
  return (
    <Section id="gallery" kicker="Фотогалерея" title="Как это выглядит">
      <div className="grid grid-cols-2 gap-4 md:grid-cols-3">
        {placeholders.map((i) => (
          <div key={i} className={`rounded-xl bg-navy-soft ${i % 3 === 0 ? 'row-span-2' : 'aspect-[4/3]'}`} />
        ))}
      </div>
    </Section>
  )
}
