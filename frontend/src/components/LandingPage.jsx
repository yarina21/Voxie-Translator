export default function LandingPage() {
  return (
    <div className="w-full min-h-screen flex flex-col justify-between py-12 px-8" style={{
      background: 'linear-gradient(135deg, #f8d7e8 0%, #fbe4ec 50%, #f8d7e8 100%)'
    }}>
      {/* Top-left Title */}
      <div className="flex justify-start">
        <h1 className="voxie-title">VOXIE AI</h1>
      </div>

      {/* Center Content */}
      <div className="flex-1 flex flex-col items-center justify-center gap-8">
        {/* Speech Bubble */}
        <div className="speech-bubble">
          <p className="speech-text">
            Bună! Sunt Voxie, asistentul tău de traducere vocală. Vorbește natural, iar eu voi traduce în timp real pentru tine. 🌸
          </p>
        </div>

        {/* Animated Robot SVG */}
        <div className="robot-animation">
          <svg viewBox="0 0 200 240" width="400" height="400" xmlns="http://www.w3.org/2000/svg">
            {/* Robot Head */}
            <rect x="60" y="40" width="80" height="80" rx="10" fill="#E8C4D9" stroke="#5a7a8f" strokeWidth="2"/>
            
            {/* Eyes */}
            <circle cx="80" cy="60" r="8" fill="#5a7a8f" className="robot-eye"/>
            <circle cx="120" cy="60" r="8" fill="#5a7a8f" className="robot-eye"/>
            
            {/* Smile */}
            <path d="M 85 80 Q 100 90 115 80" stroke="#5a7a8f" strokeWidth="2" fill="none" strokeLinecap="round"/>
            
            {/* Robot Body */}
            <rect x="70" y="130" width="60" height="70" rx="5" fill="#D4A5C4" stroke="#5a7a8f" strokeWidth="2"/>
            
            {/* Arms */}
            <rect x="30" y="145" width="40" height="15" rx="7" fill="#D4A5C4" stroke="#5a7a8f" strokeWidth="2" className="robot-arm-left"/>
            <rect x="130" y="145" width="40" height="15" rx="7" fill="#D4A5C4" stroke="#5a7a8f" strokeWidth="2" className="robot-arm-right"/>
            
            {/* Legs */}
            <rect x="80" y="205" width="12" height="30" rx="6" fill="#5a7a8f"/>
            <rect x="108" y="205" width="12" height="30" rx="6" fill="#5a7a8f"/>
          </svg>
        </div>
      </div>

      {/* Bottom CTA */}
      <div className="flex justify-center pb-8">
        <p className="cta-text">Pentru a începe, apasă o tasta</p>
      </div>
    </div>
  )
}
