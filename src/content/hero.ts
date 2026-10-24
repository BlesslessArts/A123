// Кадр первого экрана: закат и Национальная библиотека в арочном окне.
// Один и тот же кадр и кадрирование используются в Hero (CSS) и в прелоадере (SVG), чтобы переход был бесшовным.
export const HERO_IMAGE = {
  src: `${import.meta.env.BASE_URL}media/hero-sunset.webp`,
  width: 1300,
  height: 680,
  /** точка фокуса, как object-position: Библиотека чуть левее центра */
  focusX: 0.45,
  focusY: 0.4,
}

export const heroObjectPosition = `${HERO_IMAGE.focusX * 100}% ${HERO_IMAGE.focusY * 100}%`

/** Прямоугольник картинки при object-fit: cover в области w×h — для SVG <image> */
export function coverRect(w: number, h: number) {
  const k = Math.max(w / HERO_IMAGE.width, h / HERO_IMAGE.height)
  const width = HERO_IMAGE.width * k
  const height = HERO_IMAGE.height * k
  return { x: (w - width) * HERO_IMAGE.focusX, y: (h - height) * HERO_IMAGE.focusY, width, height }
}
