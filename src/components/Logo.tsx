// Временный логотип-арка. Заменим на SVG из фирменных материалов и анимируем (лоадер + hover).
export function Logo({ className = '' }: { className?: string }) {
  return (
    <span className={`group inline-flex items-center gap-2 ${className}`}>
      <svg viewBox="0 0 32 32" className="h-8 w-8" aria-hidden>
        <path
          d="M6 28V14a10 10 0 0 1 20 0v14"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          className="transition-[stroke-dashoffset] duration-700 [stroke-dasharray:80] group-hover:[stroke-dashoffset:80]"
        />
      </svg>
      <span className="font-display text-xl tracking-wide">АРКА 123</span>
    </span>
  )
}
