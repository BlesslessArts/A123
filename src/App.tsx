import { MotionConfig } from 'motion/react'
import { useState } from 'react'
import { Footer } from './components/Footer'
import { Header } from './components/Header'
import { Preloader } from './components/Preloader'
import { About } from './sections/About'
import { Gallery } from './sections/Gallery'
import { Hero } from './sections/Hero'
import { Pricing } from './sections/Pricing'
import { Reviews } from './sections/Reviews'
import { Services } from './sections/Services'
import { Space } from './sections/Space'
import { Stats } from './sections/Stats'
import { initSmoothScroll } from './lib/smooth-scroll'

export default function App() {
  // ready — прелоадер распахнул окно (или не показывался): запускаем появление первого экрана
  const [ready, setReady] = useState(false)

  return (
    <MotionConfig reducedMotion="user">
      <Preloader
        onDone={() => {
          setReady(true)
          initSmoothScroll()
        }}
      />
      <Header ready={ready} />
      <main>
        <Hero ready={ready} />
        <Stats />
        <About />
        <Space />
        <Services />
        <Gallery />
        <Pricing />
        <Reviews />
      </main>
      <Footer />
    </MotionConfig>
  )
}
