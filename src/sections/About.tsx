import { Section } from '../components/Section'

// TODO: фирменный персонаж (статичная иллюстрация) рядом с текстом
export function About() {
  return (
    <Section id="about" kicker="О нас" title="Пространство под аркой">
      <div className="grid gap-10 md:grid-cols-2">
        <p className="text-lg leading-relaxed">
          Здание на Мстиславца, 10 — это два высоких дома, соединённых аркой. Через неё с променада открывается вид на
          Национальную библиотеку. Тот же вид — из огромных арочных окон нашего зала.
        </p>
        <div className="aspect-[4/5] rounded-2xl bg-stone/60" aria-label="Место для фирменного персонажа" />
      </div>
    </Section>
  )
}
