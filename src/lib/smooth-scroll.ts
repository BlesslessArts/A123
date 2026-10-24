import Lenis from 'lenis'
import 'lenis/dist/lenis.css'

// Плавная прокрутка с инерцией (E1). На тач-устройствах Lenis не трогает нативный скролл (syncTouch: false),
// при prefers-reduced-motion не включается. Модалки (лайтбокс, прелоадер) останавливают её через lockScroll.

let lenis: Lenis | null = null

export function initSmoothScroll() {
  if (lenis || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return
  lenis = new Lenis({ autoRaf: true, lerp: 0.09, anchors: { offset: -64 } })
}

export function lockScroll(locked: boolean) {
  if (locked) lenis?.stop()
  else lenis?.start()
  document.documentElement.style.overflow = locked ? 'hidden' : ''
}
