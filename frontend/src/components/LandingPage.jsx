import { useEffect, useRef } from 'react'
// IMPORTĂM DIRECT ROBOTUL - Vite va gestiona calea corectă automat
import robotAnimation from '../assets/robot.json' 

export default function LandingPage({ onNavigate }) {
  const lottieContainerRef = useRef(null)

  // Efectul pentru animația Lottie
  useEffect(() => {
    if (window.lottie && lottieContainerRef.current) {
      const animation = window.lottie.loadAnimation({
        container: lottieContainerRef.current,
        renderer: 'svg',
        loop: true,
        autoplay: true,
        // În loc de "path" (text), îi dăm direct datele animației importate mai sus
        animationData: robotAnimation 
      })

      // Curățăm animația când ieșim de pe pagină
      return () => animation.destroy()
    }
  }, [])

  // Efectul pentru apăsarea tastei
  useEffect(() => {
    const handleKey = (e) => {
      if (onNavigate) {
        onNavigate()
      }
    }

    window.addEventListener('keydown', handleKey)
    return () => window.removeEventListener('keydown', handleKey)
  }, [onNavigate])

  return (
    <div className="w-full min-h-screen flex flex-col justify-between py-12 px-8">
      {/* Top-left Title */}
      <div className="flex justify-start">
        <h1 className="voxie-title">VOXIE AI</h1>
      </div>
      
      {/* Center Content */}
      <div className="flex-1 flex flex-col items-center justify-center gap-8">
        {/* Speech Bubble */}
        <div className="speech-bubble">
          <p className="speech-text">
            Bună! Sunt Voxie, asistentul tău de traducere vocală. <br />
            Vorbește natural, iar eu voi traduce în timp real pentru tine. 🌸
          </p>
        </div>
        
        {/* Lottie Animation Container */}
        <div ref={lottieContainerRef} id="lottie-container"
        style={{ width: '400px', height: '400px', margin: '0 auto' }}></div>
      </div>
      
      {/* Bottom CTA */}
      <div className="flex justify-center pb-8">
        <p className="cta-text">Pentru a începe, apasă o tastă</p>
      </div>
    </div>
  )
}