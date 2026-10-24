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
  return (
    <>
      <Preloader />
      <Header />
      <main>
        <Hero />
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
