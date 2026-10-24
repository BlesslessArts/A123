// Фото галереи: public/media/gallery/<id>.webp (1600px) и <id>-sm.webp (720px), исходники — materials/Фото обработанное.

export type Photo = { id: string; alt: string; portrait?: boolean }

export const galleryGroups: { id: string; label: string; photos: Photo[] }[] = [
  {
    id: 'hall',
    label: 'Зал',
    photos: [
      { id: '00', alt: 'Два арочных окна 4×3 м с видом на Национальную библиотеку на закате' },
      { id: '06', alt: 'Зал с арочными окнами и паркетом ёлочкой' },
      { id: '02', alt: 'Общий вид зала, высота потолка до 4,5 метров' },
      { id: '07', alt: 'Вид на Национальную библиотеку из арочного окна', portrait: true },
      { id: '01', alt: 'Светлый зал с колоннами и часами на стене' },
      { id: '05', alt: 'Угол зала с двумя арочными окнами', portrait: true },
      { id: '03', alt: 'Характеристики помещения: пол, стены, потолок, освещение', portrait: true },
      { id: '08', alt: 'Арочное окно с видом на променад', portrait: true },
      { id: '04', alt: 'Зал вдоль окон', portrait: true },
      { id: '09', alt: 'Арочное окно с логотипом на стекле', portrait: true },
      { id: '10', alt: 'Зал с часами и потолочными светильниками', portrait: true },
      { id: '11', alt: 'Зона ресепшена у входа', portrait: true },
    ],
  },
  {
    id: 'details',
    label: 'Вход и детали',
    photos: [
      { id: '12', alt: 'Стеклянные перегородки и шкафы у входа' },
      { id: '13', alt: 'Входная группа со стеклянными дверями' },
      { id: '14', alt: 'Коридор у входа в зал', portrait: true },
    ],
  },
  {
    id: 'outside',
    label: 'Как нас найти',
    photos: [
      { id: '15', alt: 'Фасад здания с арочными окнами АРКА 123' },
      { id: '16', alt: 'Променад вдоль здания' },
      { id: '19', alt: 'Здание из двух домов, соединённых аркой, вид с дороги' },
      { id: '20', alt: 'Здание и парковка перед ним' },
      { id: '21', alt: 'Перекрёсток у здания, вид на Национальную библиотеку' },
      { id: '17', alt: 'Улица у здания', portrait: true },
      { id: '18', alt: 'Угол здания с арочными окнами', portrait: true },
    ],
  },
]

export const photoUrl = (id: string, small = false) =>
  `${import.meta.env.BASE_URL}media/gallery/${id}${small ? '-sm' : ''}.webp`
