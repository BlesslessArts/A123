import { AnimatePresence, motion } from 'motion/react'
import { useCallback, useEffect, useState } from 'react'
import { ArchReveal } from '../components/ArchReveal'
import { Section } from '../components/Section'
import { galleryGroups, photoUrl } from '../content/gallery'
import { lockScroll } from '../lib/smooth-scroll'

// Сколько фото показывать до «Показать все», чтобы блок не растягивался на несколько экранов
const PREVIEW_COUNT = 6

export function Gallery() {
  const [groupId, setGroupId] = useState(galleryGroups[0].id)
  const [open, setOpen] = useState<number | null>(null)
  const [showAll, setShowAll] = useState(false)
  const photos = galleryGroups.find((g) => g.id === groupId)!.photos

  const step = useCallback(
    (d: number) => setOpen((i) => (i === null ? i : (i + d + photos.length) % photos.length)),
    [photos.length],
  )

  useEffect(() => {
    if (open === null) return
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setOpen(null)
      if (e.key === 'ArrowRight') step(1)
      if (e.key === 'ArrowLeft') step(-1)
    }
    lockScroll(true)
    window.addEventListener('keydown', onKey)
    return () => {
      lockScroll(false)
      window.removeEventListener('keydown', onKey)
    }
  }, [open, step])

  return (
    <Section id="gallery" kicker="Фотогалерея" title="Как это выглядит">
      <div className="mb-8 flex flex-wrap gap-2">
        {galleryGroups.map((g) => (
          <button
            key={g.id}
            onClick={() => (setGroupId(g.id), setShowAll(false))}
            className={`rounded-full border px-4 py-2 text-sm transition-colors ${
              g.id === groupId ? 'border-sunset bg-sunset text-night' : 'border-plaster/30 hover:border-plaster'
            }`}
          >
            {g.label} <span className="opacity-60">{g.photos.length}</span>
          </button>
        ))}
      </div>

      <div className="columns-2 gap-4 md:columns-3">
        {(showAll ? photos : photos.slice(0, PREVIEW_COUNT)).map((p, i) => (
          <button
            key={p.id}
            onClick={() => setOpen(i)}
            className="group mb-4 block w-full"
          >
            <ArchReveal delay={(i % 3) * 0.1} className="bg-navy-soft">
              <img
                src={photoUrl(p.id, true)}
                alt={p.alt}
                width={p.portrait ? 405 : 720}
                height={p.portrait ? 720 : 405}
                loading="lazy"
                className="h-auto w-full transition-transform duration-700 group-hover:scale-105"
              />
            </ArchReveal>
          </button>
        ))}
      </div>

      {!showAll && photos.length > PREVIEW_COUNT && (
        <button
          onClick={() => setShowAll(true)}
          className="mx-auto mt-4 block rounded-full border border-plaster/30 px-6 py-3 text-sm hover:border-sunset hover:text-sunset"
        >
          Показать все {photos.length} фото
        </button>
      )}

      <AnimatePresence>
        {open !== null && (
          <motion.div
            className="fixed inset-0 z-50 flex items-center justify-center bg-night/95 p-4"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setOpen(null)}
            role="dialog"
            aria-modal="true"
            aria-label={photos[open].alt}
          >
            <motion.img
              key={photos[open].id}
              src={photoUrl(photos[open].id)}
              alt={photos[open].alt}
              className="max-h-[85vh] max-w-full rounded-lg object-contain"
              initial={{ opacity: 0, scale: 0.97 }}
              animate={{ opacity: 1, scale: 1 }}
              drag="x"
              dragConstraints={{ left: 0, right: 0 }}
              onDragEnd={(_, info) => {
                if (Math.abs(info.offset.x) > 80) step(info.offset.x < 0 ? 1 : -1)
              }}
              onClick={(e) => e.stopPropagation()}
            />
            <p className="absolute inset-x-0 bottom-4 text-center text-sm text-plaster/70">
              {photos[open].alt} · {open + 1}/{photos.length}
            </p>
            <button
              onClick={(e) => (e.stopPropagation(), step(-1))}
              className="absolute left-2 top-1/2 hidden -translate-y-1/2 p-4 text-4xl text-plaster/70 hover:text-sunset sm:block"
              aria-label="Предыдущее фото"
            >
              ‹
            </button>
            <button
              onClick={(e) => (e.stopPropagation(), step(1))}
              className="absolute right-2 top-1/2 hidden -translate-y-1/2 p-4 text-4xl text-plaster/70 hover:text-sunset sm:block"
              aria-label="Следующее фото"
            >
              ›
            </button>
            <button
              onClick={() => setOpen(null)}
              className="absolute right-4 top-4 p-2 text-3xl text-plaster/70 hover:text-sunset"
              aria-label="Закрыть"
            >
              ×
            </button>
          </motion.div>
        )}
      </AnimatePresence>
    </Section>
  )
}
