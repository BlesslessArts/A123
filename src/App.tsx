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

export default function App() {
  // ready — прелоадер распахнул окно (или не показывался): запускаем появление первого экрана
  const [ready, setReady] = useState(false)

  return (
    <>
      <Preloader onDone={() => setReady(true)} />
      <Header ready={ready} />
      <main>
        <Hero ready={ready} />
        <About />
        <Space />
        <Services />
        <Gallery />
        <Pricing />
        <Reviews />
      </main>
      <Footer />
    </>
  )
}
